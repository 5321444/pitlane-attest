const file = document.getElementById("file");
const grid = document.getElementById("grid");
const statusEl = document.getElementById("status");

function cell(k, v){
  const c = document.createElement("div");
  c.className = "cell";
  const kEl = document.createElement("div"); kEl.className = "key"; kEl.textContent = k;
  const vEl = document.createElement("div"); vEl.className = "val"; vEl.textContent = v;
  c.appendChild(kEl); c.appendChild(vEl); return c;
}

file.addEventListener("change", async (e) => {
  grid.innerHTML = "";
  const f = e.target.files?.[0];
  if(!f){ statusEl.textContent = "No file loaded."; return; }
  try{
    const text = await f.text();
    const data = JSON.parse(text);
    statusEl.textContent = "Loaded.";
    const fields = [
      ["schema", data.schema],
      ["action_id", data.action_id],
      ["agent_id", data.agent_id],
      ["policy_id", data.policy_id],
      ["env", data.env],
      ["risk", data.risk],
      ["timestamp", String(data.timestamp)],
      ["telemetry.kind", data.telemetry?.kind],
      ["telemetry.path", data.telemetry?.path],
      ["telemetry.sha256", data.telemetry?.sha256],
      ["signer_pub", data.signer_pub],
      ["signature", data.signature?.slice(0,32) + "…"],
      ["notes", data.notes ?? ""],
    ];
    fields.forEach(([k,v]) => grid.appendChild(cell(k, v ?? "")));
  }catch(err){
    statusEl.textContent = "Failed to parse JSON.";
  }
});
