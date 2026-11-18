const tokenKey = "fv-bench-admin-token";
const $ = (id) => document.getElementById(id);
let busy = false;

function token() {
  return sessionStorage.getItem(tokenKey) || "";
}

function showAuth(message = "") {
  $("auth-error").textContent = message;
  $("auth-overlay").hidden = false;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Authorization": `Bearer ${token()}`, "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const body = await response.json();
  if (response.status === 401) {
    sessionStorage.removeItem(tokenKey);
    showAuth("Token rejected. Check FV_ADMIN_TOKEN and try again.");
    throw new Error("Admin token rejected. Clear it and enter the configured token again.");
  }
  if (!response.ok) throw new Error(body.error || `Request failed (${response.status})`);
  return body;
}

function setBusy(value) {
  busy = value;
  document.querySelectorAll("button").forEach((button) => { button.disabled = value; });
}

async function send(action, reason = "", pulseUs = undefined) {
  if (busy) return;
  setBusy(true);
  try {
    await api("/api/command", { method: "POST", body: JSON.stringify({ action, reason, pulse_us: pulseUs }) });
    await refresh();
  } catch (error) {
    window.alert(error.message);
  } finally {
    setBusy(false);
  }
}

function renderLog(commands) {
  const root = $("log");
  root.replaceChildren();
  if (!commands.length) {
    const empty = document.createElement("div"); empty.className = "empty"; empty.textContent = "No commands yet."; root.append(empty); return;
  }
  for (const command of commands.slice(0, 20)) {
    const row = document.createElement("div"); row.className = "entry";
    const left = document.createElement("strong"); left.textContent = `${command.action || "command"} · ${command.state || "sent"}`;
    const right = document.createElement("span"); right.textContent = command.reason || command.detail || command.command_id || "";
    row.append(left, right); root.append(row);
  }
}

async function refresh() {
  if (!token()) { showAuth(); return false; }
  try {
    const snapshot = await api("/api/snapshot");
    $("device-tag").textContent = snapshot.device_id;
    $("broker").textContent = snapshot.broker;
    const online = snapshot.availability === "online";
    $("availability").replaceChildren();
    const dot = document.createElement("i"); dot.className = `dot ${online ? "online" : snapshot.availability === "offline" ? "offline" : ""}`;
    $("availability").append(dot, document.createTextNode(snapshot.availability));
    const status = snapshot.status || {};
    const ip = status.ip ? ` · ${status.ip}` : "";
    const reset = status.reset_reason !== undefined ? ` · reset reason ${status.reset_reason}` : "";
    $("device-meta").textContent = `${status.firmware || "Waiting for retained MQTT status"}${ip}${reset}`;
    $("pulse").textContent = status.pulse_us === undefined ? "— µs" : `${status.pulse_us} µs`;
    $("output").textContent = status.output_enabled === undefined ? "Output state unknown" : `PWM ${status.output_enabled ? "enabled" : "disabled"}`;
    $("last-update").textContent = snapshot.updated_at ? `Last device update: ${new Date(snapshot.updated_at).toLocaleString()}` : "No device update yet";
    renderLog(snapshot.commands || []);
    return true;
  } catch (error) {
    if (error.message.includes("Admin token")) return false;
    $("broker").textContent = "Dashboard error";
    $("device-meta").textContent = error.message;
    return false;
  }
}

document.querySelectorAll("[data-action]").forEach((button) => button.addEventListener("click", () => send(button.dataset.action, "bench dashboard")));
$("set-pulse").addEventListener("click", () => {
  const pulse = Number($("pulse-input").value);
  if (!Number.isInteger(pulse) || pulse < 1000 || pulse > 2000) return window.alert("Use an integer from 1000 to 2000 µs.");
  send("servo.set", "bench dashboard pulse test", pulse);
});
$("restart").addEventListener("click", () => {
  const reason = $("reason").value.trim();
  if (reason.length < 3) return window.alert("Enter a reason for this restart.");
  if (window.confirm(`Restart ${$("device-tag").textContent}? The servo PWM will be disabled, then boot reapplies center pulse.`)) send("restart", reason);
});
$("auth-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  sessionStorage.setItem(tokenKey, $("admin-token").value.trim());
  if (await refresh()) $("auth-overlay").hidden = true;
});
$("logout").addEventListener("click", () => { sessionStorage.removeItem(tokenKey); showAuth("Admin token cleared."); });
refresh();
window.setInterval(refresh, 1200);
