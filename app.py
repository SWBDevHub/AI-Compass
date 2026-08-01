import uuid
from flask import Flask, render_template, request, send_file, redirect, url_for
from services import compass_service, docx_service, db_service

app = Flask(__name__)

# SQLite persistence — replaces the v0.1 in-memory dict.
# Creates aicompass.db (and the table, if missing) on startup.
db_service.init_db()


@app.route("/")
def index():
    """Intake form — the business user starts here."""
    return render_template("index.html")


@app.route("/evaluate", methods=["POST"])
def evaluate():
    intake = {
        "business_problem": request.form.get("business_problem", ""),
        "proposed_tool": request.form.get("proposed_tool", ""),
        "data_sensitivity": request.form.get("data_sensitivity", ""),
        "users_affected": request.form.get("users_affected", ""),
        "expected_value": request.form.get("expected_value", ""),
        "estimated_usage": request.form.get("estimated_usage", ""),
        "decision_impact": request.form.getlist("decision_impact"),
    }
    try:
        result = compass_service.evaluate(intake)
    except ValueError as e:
        return render_template("intake_debug.html", intake={"ERROR": str(e)})

    governance = result.get("governance_decision", {})
    decision_value = governance.get("decision")

    eval_id = str(uuid.uuid4())
    db_service.save_evaluation(
        eval_id, intake, result, decision_value, compass_service.decision_class(decision_value)
    )

    # POST-redirect-GET: after submitting, redirect to a real URL for this
    # evaluation rather than rendering results directly. This is what makes
    # the results page revisitable/bookmarkable/linkable from the dashboard,
    # and avoids the classic "refresh resubmits the form" problem.
    return redirect(url_for("view_results", eval_id=eval_id))


@app.route("/results/<eval_id>")
def view_results(eval_id):
    record = db_service.get_evaluation(eval_id)
    if not record:
        return "Evaluation not found.", 404

    result = record["result"]
    governance = result.get("governance_decision", {})

    return render_template(
        "results.html",
        governance=governance,
        risks=result.get("risk_assessment", {}),
        plan=result.get("evaluation_plan", {}),
        decision_class=record["decision_class"],
        eval_id=eval_id,
    )


@app.route("/download/<eval_id>")
def download(eval_id):
    record = db_service.get_evaluation(eval_id)
    if not record:
        return "Evaluation not found.", 404

    buffer = docx_service.build_evidence_pack(record["intake"], record["result"])
    return send_file(
        buffer,
        as_attachment=True,
        download_name="AI_Compass_Evidence_Pack.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@app.route("/dashboard")
def dashboard():
    status_filter = request.args.get("status")

    all_evaluations = db_service.list_evaluations()

    counts = {}
    for e in all_evaluations:
        counts[e["decision"]] = counts.get(e["decision"], 0) + 1

    evaluations = all_evaluations
    if status_filter:
        evaluations = [e for e in all_evaluations if e["decision"] == status_filter]

    return render_template(
        "dashboard.html",
        evaluations=evaluations,
        counts=counts,
        active_filter=status_filter,
        total=len(all_evaluations),
    )


if __name__ == "__main__":
    app.run(debug=True)
