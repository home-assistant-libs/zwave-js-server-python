import { getAllNotifications, getAllSensors } from "@zwave-js/core";
import fs from "fs";

for (const [filename, data] of Object.entries({
  "notifications.json": getAllNotifications(),
  "sensors.json": getAllSensors(),
})) {
  if (fs.existsSync(filename)) {
    fs.unlinkSync(filename);
  }
  fs.writeFileSync(
    filename,
    JSON.stringify(data, (_: any, value: any) =>
      value instanceof Map ? Object.fromEntries(value) : value
    )
  );
}
