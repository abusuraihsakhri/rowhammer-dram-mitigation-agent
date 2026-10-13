"use strict";

// Pure, deterministic browser demonstration corresponding to agents/workers.py.
// It is not a model of DRAM physics and does not generate HMAC signatures.
function validate(raw) {
  const task_id = String(raw.task_id || "").trim();
  const target_identifier = String(raw.target_identifier || "").trim();
  const status_descriptor = String(raw.status_descriptor || "").trim();
  if (!task_id || task_id.length > 128) throw new Error("Task identifier must have 1–128 characters.");
  if (!target_identifier || target_identifier.length > 128) throw new Error("Target identifier must have 1–128 characters.");
  if (status_descriptor.length > 64) throw new Error("Status descriptor cannot exceed 64 characters.");
  const primary_metric = Number(raw.primary_metric);
  const secondary_metric = Number(raw.secondary_metric);
  if (String(raw.primary_metric).trim() === "" || !Number.isFinite(primary_metric) ||
      primary_metric < -1000 || primary_metric > 1000) {
    throw new Error("Primary indicator must be a finite number between -1000 and 1000.");
  }
  if (String(raw.secondary_metric).trim() === "" || !Number.isFinite(secondary_metric) ||
      secondary_metric < -1000 || secondary_metric > 1000) {
    throw new Error("Secondary indicator must be a finite number between -1000 and 1000.");
  }
  return {task_id, target_identifier, primary_metric, secondary_metric,
    status_descriptor, is_critical_flag: raw.is_critical_flag === true};
}

function evaluate(raw) {
  const value = validate(raw);
  const alerts = [];
  if (value.primary_metric > 25) {
    alerts.push({worker:"InvariantQCWorker",urgency:"ELEVATED_RISK",
      summary:"Primary indicator exceeds illustrative threshold (25)."});
  }
  if (value.is_critical_flag || value.secondary_metric > 12) {
    alerts.push({worker:"SafetyEscalationWorker",
      urgency:value.is_critical_flag ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
      summary:"Explicit critical flag or secondary indicator above 12."});
  }
  if (/(DISCORDANT|ANOMALY|MUTANT|VIOLATION|FAIL|REJECT)/i.test(value.status_descriptor)) {
    alerts.push({worker:"ProtocolConformanceWorker",urgency:"ELEVATED_RISK",
      summary:"Status descriptor matches an anomaly keyword."});
  }
  const critical = alerts.some(a => a.urgency === "CRITICAL_STAT_PANIC");
  const elevated = alerts.length > 0;
  const overall_urgency = critical ? "CRITICAL_STAT_PANIC" : elevated ? "ELEVATED_RISK" : "ROUTINE";
  return {model:"Illustrative numeric threshold classifier; not validated against hardware",
    task_id:value.task_id, target_identifier:value.target_identifier,
    indicators:{primary_metric:value.primary_metric,secondary_metric:value.secondary_metric,
      status_descriptor:value.status_descriptor,is_critical_flag:value.is_critical_flag},
    overall_urgency,
    integrity_status:critical ? "RECALIBRATION_REQUIRED" : elevated ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL",
    total_alerts:alerts.length, critical_alerts_count:alerts.filter(a => a.urgency === "CRITICAL_STAT_PANIC").length,
    alerts, audited:false, hmac_signed:false};
}

if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => {
    let latest = null, count = 0, criticalCount = 0;
    const el = id => document.getElementById(id);
    el("auditForm").addEventListener("submit", event => {
      event.preventDefault();
      el("error").textContent = "";
      try {
        latest = evaluate({
          task_id:el("task_id").value,
          target_identifier:el("target_id").value,
          primary_metric:el("primary_metric").value,
          secondary_metric:el("secondary_metric").value,
          status_descriptor:el("status_descriptor").value,
          is_critical_flag:el("is_critical").checked
        });
        count++;
        if (latest.overall_urgency === "CRITICAL_STAT_PANIC") criticalCount++;
        el("m-tasks").textContent = String(count);
        el("m-critical").textContent = String(criticalCount);
        el("m-status").textContent = latest.overall_urgency === "CRITICAL_STAT_PANIC" ? "CRITICAL" :
          latest.overall_urgency === "ELEVATED_RISK" ? "ELEVATED" : "ROUTINE";
        el("outputConsole").textContent = JSON.stringify(latest, null, 2);
        el("download").disabled = false;
      } catch (error) {
        el("error").textContent = error.message;
      }
    });
    el("download").addEventListener("click", () => {
      if (!latest) return;
      const blob = new Blob([JSON.stringify(latest, null, 2) + "\n"], {type:"application/json"});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "rowhammer-indicator-result.json";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    });
  });
}
if (typeof module !== "undefined" && module.exports) module.exports = {validate, evaluate};
