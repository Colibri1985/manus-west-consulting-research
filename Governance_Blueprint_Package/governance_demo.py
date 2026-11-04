import json, hashlib
from pathlib import Path

def canonical(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()

def digest(x):
    return hashlib.sha256(canonical(x)).hexdigest()

def build(rules, approvals, project, task, role):
    selected = []
    for r in rules:
        if r["status"] != "approved":
            continue
        if r.get("project_id") not in (None, project):
            continue
        if r.get("task_id") not in (None, task):
            continue
        if role not in r["roles"] and "*" not in r["roles"]:
            continue
        if digest(r) not in approvals:
            raise ValueError("Missing trusted digest approval: " + r["rule_id"])
        if r["effect"] not in ("deny", "require", "allow"):
            raise ValueError("Unknown effect")
        selected.append(r)
    baseline = {(r["resource"],r["action"]) for r in selected
                if r["layer"] == "global" and r["effect"] == "deny"}
    for r in selected:
        if r["effect"] == "allow":
            raise ValueError("Grant rules unsupported in strict demo: " + r["rule_id"])
    if not baseline:
        raise ValueError("No applicable baseline deny in demo")
    selected.sort(key=lambda r:(r["layer"],r["rule_id"],r["revision"]))
    manifest = {"project":project,"task":task,"role":role,
                "rules":[{"id":r["rule_id"],"revision":r["revision"],
                          "sha256":digest(r)} for r in selected]}
    manifest["bundle_id"] = digest(manifest)
    return selected,manifest

def main():
    base = {"rule_id":"GLOBAL.DELETE","revision":1,"layer":"global",
            "project_id":None,"task_id":None,"roles":["*"],
            "status":"approved","effect":"deny","resource":"workspace",
            "action":"delete","statement":"No unapproved workspace deletion"}
    project = {"rule_id":"MOEX.PROVENANCE","revision":1,"layer":"project",
               "project_id":"moex","task_id":None,"roles":["developer","qa"],
               "status":"approved","effect":"require","resource":"fact",
               "action":"modify","statement":"Preserve evidence provenance"}
    proposal = dict(project,rule_id="MOEX.DRAFT",status="proposed")
    approvals = {digest(base),digest(project)}
    rules,manifest = build([base,project,proposal],approvals,"moex","FIN-001","developer")
    assert len(rules)==2
    changed=dict(project,statement="Tampered")
    try:
        build([base,changed],approvals,"moex","FIN-001","developer")
        raise AssertionError("Tampering accepted")
    except ValueError:
        pass
    grant=dict(project,rule_id="MOEX.GRANT",effect="allow",resource="workspace",action="delete")
    try:
        build([base,grant],approvals|{digest(grant)},"moex","FIN-001","developer")
        raise AssertionError("Grant accepted")
    except ValueError:
        pass
    out=Path("demo-bundle")
    out.mkdir(exist_ok=True)
    (out/"manifest.json").write_bytes(canonical(manifest))
    (out/"rules.md").write_text("\n\n".join(r["rule_id"]+": "+r["statement"] for r in rules))
    print(json.dumps({"bundle_id":manifest["bundle_id"],"selected":len(rules),"negative_tests":"passed"}))

if __name__ == "__main__":
    main()
