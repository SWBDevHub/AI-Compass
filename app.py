import uuid
from flask import Flask, render_template, request, send_file
from services import compass_service, docx_service

app = Flask(__name__)

# In-memory store, keyed by a random ID per evaluation.
# No database in v0.1 — this resets whenever the server restarts,
# which is an accepted tradeoff at this stage, not a bug.
EVALUATIONS = {}


@app.route("/")
def index():
    """Intake form — the business user starts here."""
    return render_template("index.html")


@app.route("/evaluate", methods=["POST"])
def evaluate():
    """
    Step 1 placeholder: just capture and echo the form data back
    so we can confirm the intake form is wired correctly before
    we plug in the Claude call in step 2.
    """
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

    decision = result.get("governance_decision", {})
    decision_class_map = {
        "approve": "success",
        "approve_with_controls": "warning",
        "pilot_only": "warning",
        "reject": "danger",
        "escalate_legal_security": "danger",
    }
    decision_class = decision_class_map.get(decision.get("decision"), "warning")

    eval_id = str(uuid.uuid4())
    EVALUATIONS[eval_id] = {"intake": intake, "result": result}

    return render_template(
        "results.html",
        governance=decision,
        risks=result.get("risk_assessment", {}),
        plan=result.get("evaluation_plan", {}),
        decision_class=decision_class,
        eval_id=eval_id,
    )


@app.route("/download/<eval_id>")
def download(eval_id):
    """Regenerates the .docx evidence pack on demand from the in-memory store."""
    data = EVALUATIONS.get(eval_id)
    if not data:
        return "Evaluation not found — it may have expired or the server restarted.", 404

    buffer = docx_service.build_evidence_pack(data["intake"], data["result"])
    return send_file(
        buffer,
        as_attachment=True,
        download_name="AI_Compass_Evidence_Pack.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


if __name__ == "__main__":
    app.run(debug=True)
