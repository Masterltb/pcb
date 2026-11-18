# MQTT reset test for the Rev-S3 S1 bench firmware

This firmware targets the ESP32-S3 bench fixture in `servo_s1_bench`, not a production
FreshVend controller. It performs a CPU restart only; it does not power-cycle the PCB
or repair a brownout, blocked servo, or wiring fault. The existing boot behavior sets
GPIO16 to the bench firmware's 1500 µs center pulse, so test with the servo unloaded
or mechanically safe.

## Configure and flash

1. Copy `secrets.example.h` to `secrets.h` and set the test Wi-Fi, broker, username,
   password, and broker root CA. The local `secrets.h` is ignored by Git.
2. Create a broker user with TLS enabled and ACLs limited to:
   - subscribe: `freshvend/rev-s3-s1-bench-01/admin/command`
   - publish: `freshvend/rev-s3-s1-bench-01/admin/ack`,
     `freshvend/rev-s3-s1-bench-01/status`,
     `freshvend/rev-s3-s1-bench-01/availability`
3. Build and flash using PlatformIO. Do not publish retained messages to the command
   topic. The firmware also rejects commands older than 60 seconds and persists the
   last command ID to reject QoS 1 replay across a reboot.

## Send a test command

In MQTTX or another authenticated MQTT client, connect over TLS, subscribe to
`freshvend/rev-s3-s1-bench-01/#`, and publish to
`freshvend/rev-s3-s1-bench-01/admin/command` with QoS 1 and retain disabled:

```json
{"device_id":"rev-s3-s1-bench-01","command_id":"test-20261118-001","action":"restart","issued_at":1794960000}
```

Replace `issued_at` with the current Unix time in seconds (PowerShell:
`[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()`). It must be within 60 seconds of
the board clock.
Expect an `accepted` ACK, then a `restarting` ACK, an offline/online availability
transition, and a retained status after reconnect. The Serial Monitor also reports
the command ID. A repeated ID is rejected; use a new ID for each intentional reset.

For the local bench dashboard, follow `dashboard/README.md`. The Python bridge holds
MQTT credentials and serves the UI on loopback. It sends non-retained commands for
servo test, status, and restart, and displays ACK/availability. The dashboard uses a
single local admin token; it is not the production user/role or audit service.
