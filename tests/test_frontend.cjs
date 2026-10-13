"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const {evaluate, validate} = require("../web/app.js");
const baseline = {task_id:"T1",target_identifier:"D1",primary_metric:12,secondary_metric:4,
  status_descriptor:"NOMINAL",is_critical_flag:false};

test("nominal inputs produce no alerts or fabricated signing", () => {
  const result = evaluate(baseline);
  assert.equal(result.overall_urgency, "ROUTINE");
  assert.equal(result.total_alerts, 0);
  assert.equal(result.hmac_signed, false);
  assert.equal(Object.hasOwn(result, "audit_hash"), false);
});
test("primary threshold and secondary threshold are strict", () => {
  assert.equal(evaluate({...baseline,primary_metric:25}).total_alerts,0);
  assert.equal(evaluate({...baseline,primary_metric:25.01}).total_alerts,1);
  assert.equal(evaluate({...baseline,secondary_metric:12.01}).overall_urgency,"ELEVATED_RISK");
});
test("critical flag wins over elevated indicators", () => {
  const r=evaluate({...baseline,primary_metric:30,is_critical_flag:true,status_descriptor:"DISCORDANT"});
  assert.equal(r.overall_urgency,"CRITICAL_STAT_PANIC");
  assert.equal(r.total_alerts,3);
  assert.equal(r.critical_alerts_count,1);
});
test("invalid and non-finite values are rejected", () => {
  assert.throws(() => validate({...baseline,primary_metric:""}),/finite number/);
  assert.throws(() => validate({...baseline,secondary_metric:"NaN"}),/finite number/);
  assert.throws(() => validate({...baseline,task_id:"  "}),/Task identifier/);
  assert.throws(() => validate({...baseline,primary_metric:2000}),/finite number/);
});
test("anomaly descriptor triggers elevated classification", () => {
  assert.equal(evaluate({...baseline,status_descriptor:"ANOMALY"}).overall_urgency,"ELEVATED_RISK");
});
