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

const actionNames = {
  restart: "Khởi động lại CPU",
  status: "Làm mới trạng thái",
  "servo.center": "Servo về giữa",
  "servo.off": "Tắt PWM",
  "servo.on": "Bật PWM",
  "servo.set": "Đặt độ rộng xung",
};
const stateNames = {
  sent: "Đã gửi",
  done: "Hoàn tất",
  accepted: "Đã nhận lệnh",
  restarting: "Đang khởi động lại",
  duplicate: "Lệnh trùng",
  rejected: "Bị từ chối",
  failed: "Gửi thất bại",
};

function brokerLabel(value) {
  if (value === "online") return "Đã kết nối";
  if (value === "connecting") return "Đang kết nối";
  if (value.startsWith("offline")) return `Mất kết nối${value.slice("offline".length)}`;
  if (value.startsWith("connect error")) return "Lỗi kết nối MQTT";
  if (value.includes("invalid MQTT payload")) return "Nhận được dữ liệu MQTT không hợp lệ";
  return value;
}

function resetReasonLabel(value) {
  const names = {
    0: "Không xác định", 1: "Cấp nguồn", 2: "Reset ngoài",
    3: "Reset phần mềm", 4: "Lỗi panic", 5: "Watchdog ngắt",
    6: "Watchdog tác vụ", 7: "Watchdog", 8: "Thoát deep sleep",
    9: "Brownout / sụt áp", 10: "Reset SDIO",
  };
  if (value === "power_on") return "Cấp nguồn";
  if (value === "software_restart") return "Reset phần mềm";
  return names[value] || `Mã ${value}`;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Authorization": `Bearer ${token()}`, "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const body = await response.json();
  if (response.status === 401) {
    sessionStorage.removeItem(tokenKey);
    showAuth("Mã không đúng. Kiểm tra FV_ADMIN_TOKEN rồi thử lại.");
    throw new Error("Mã quản trị không hợp lệ. Hãy nhập lại mã đã cấu hình.");
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
    const empty = document.createElement("div"); empty.className = "empty"; empty.textContent = "Chưa có lệnh nào."; root.append(empty); return;
  }
  for (const command of commands.slice(0, 20)) {
    const row = document.createElement("div"); row.className = "entry";
    const left = document.createElement("strong"); left.textContent = `${actionNames[command.action] || "Lệnh"} · ${stateNames[command.state] || command.state || "Đã gửi"}`;
    const right = document.createElement("span"); right.textContent = command.reason || command.detail || command.command_id || "";
    row.append(left, right); root.append(row);
  }
}

async function refresh() {
  if (!token()) { showAuth(); return false; }
  try {
    const snapshot = await api("/api/snapshot");
    $("device-tag").textContent = snapshot.device_id;
    $("broker").textContent = brokerLabel(snapshot.broker);
    $("broker-meta").textContent = snapshot.tls_enabled
      ? "Kết nối TLS · thông tin broker chỉ lưu ở backend"
      : "MQTT nội bộ trong mạng Docker demo · không mở cổng ra máy chủ";
    const online = snapshot.availability === "online";
    const availabilityName = { online: "Đang hoạt động", offline: "Ngoại tuyến", unknown: "Chưa rõ" }[snapshot.availability] || snapshot.availability;
    $("availability").replaceChildren();
    const dot = document.createElement("i"); dot.className = `dot ${online ? "online" : snapshot.availability === "offline" ? "offline" : ""}`;
    $("availability").append(dot, document.createTextNode(availabilityName));
    const status = snapshot.status || {};
    const ip = status.ip ? ` · ${status.ip}` : "";
    const firmware = status.firmware ? (status.firmware.startsWith("demo-simulator") ? "Thiết bị mô phỏng" : `Firmware ${status.firmware}`) : "Đang chờ trạng thái MQTT từ board";
    const reset = status.reset_reason !== undefined ? ` · nguyên nhân khởi động: ${resetReasonLabel(status.reset_reason)}` : "";
    $("device-meta").textContent = `${firmware}${ip}${reset}`;
    $("pulse").textContent = status.pulse_us === undefined ? "— µs" : `${status.pulse_us} µs`;
    $("output").textContent = status.output_enabled === undefined ? "Chưa rõ trạng thái PWM" : `PWM ${status.output_enabled ? "đang bật" : "đã tắt"}`;
    $("last-update").textContent = snapshot.updated_at ? `Cập nhật gần nhất: ${new Date(snapshot.updated_at).toLocaleString("vi-VN")}` : "Chưa có cập nhật từ board";
    renderLog(snapshot.commands || []);
    return true;
  } catch (error) {
    if (error.message.includes("quản trị")) return false;
    $("broker").textContent = "Lỗi dashboard";
    $("device-meta").textContent = error.message;
    return false;
  }
}

document.querySelectorAll("[data-action]").forEach((button) => button.addEventListener("click", () => send(button.dataset.action, "Dashboard thử nghiệm")));
$("set-pulse").addEventListener("click", () => {
  const pulse = Number($("pulse-input").value);
  if (!Number.isInteger(pulse) || pulse < 1000 || pulse > 2000) return window.alert("Nhập số nguyên từ 1000 đến 2000 µs.");
  send("servo.set", "Thử độ rộng xung trên bàn thử", pulse);
});
$("restart").addEventListener("click", () => {
  const reason = $("reason").value.trim();
  if (reason.length < 3) return window.alert("Hãy nhập lý do khởi động lại.");
  if (window.confirm(`Khởi động lại ${$("device-tag").textContent}? PWM servo sẽ tắt; khi boot, firmware phát lại xung giữa 1500 µs.`)) send("restart", reason);
});
$("auth-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  sessionStorage.setItem(tokenKey, $("admin-token").value.trim());
  if (await refresh()) $("auth-overlay").hidden = true;
});
$("logout").addEventListener("click", () => { sessionStorage.removeItem(tokenKey); showAuth("Đã xóa mã quản trị khỏi phiên này."); });
refresh();
window.setInterval(refresh, 1200);
