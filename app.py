
import streamlit as st
from datetime import datetime, date

st.set_page_config(
    page_title="Post-Operative Patient Monitor",
    page_icon="🩺",
    layout="wide"
)

# ---------- Initialize demo data ----------
defaults = {
    "patient_name": "",
    "patient_id": "P001",
    "medications": [],
    "symptoms": [],
    "questions": [
        {"question": "Do you have any swelling?", "type": "Yes/No"},
        {"question": "Do you have a fever?", "type": "Yes/No"},
        {"question": "Describe any other symptoms", "type": "Text"}
    ],
    "next_med_id": 1
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------- Helpers ----------
def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def medication_status(med):
    if med["taken"]:
        return "Confirmed"
    if datetime.now().strftime("%H:%M") > med["time"]:
        return "Not confirmed - time passed"
    return "Upcoming"


# ---------- Header ----------
st.title("🩺 Post-Operative Patient Monitoring System")
st.caption("Remote follow-up for patients after surgery")

st.warning(
    "Educational prototype only. Use fictional data. "
    "This system does not provide medical advice."
)

page = st.sidebar.radio(
    "Navigation",
    ["Patient Portal", "Doctor Dashboard"]
)

st.sidebar.divider()
st.sidebar.caption("Prototype version — one shared demo session")

# ==================================================
# PATIENT PORTAL
# ==================================================
if page == "Patient Portal":
    st.header("👤 Patient Portal")

    with st.form("patient_profile"):
        name = st.text_input(
            "Patient name (fictional)",
            value=st.session_state.patient_name
        )
        patient_id = st.text_input(
            "Demo patient ID",
            value=st.session_state.patient_id
        )
        save_profile = st.form_submit_button("Save profile")

    if save_profile:
        st.session_state.patient_name = name.strip()
        st.session_state.patient_id = patient_id.strip()
        st.success("Demo profile saved.")

    st.divider()
    st.header("💊 My Medication Schedule")

    meds = st.session_state.medications

    if not meds:
        st.info("No medications have been prescribed in this demo yet.")
    else:
        confirmed = sum(1 for m in meds if m["taken"])
        adherence = round(confirmed / len(meds) * 100)

        col1, col2 = st.columns(2)
        col1.metric("Confirmed doses", f"{confirmed}/{len(meds)}")
        col2.metric("Demo confirmation rate", f"{adherence}%")

        st.caption(
            "This percentage reflects confirmations in the current session, "
            "not independently verified medication use."
        )

        for med in meds:
            with st.container(border=True):
                st.subheader(med["name"])
                st.write("Prescribed dose:", med["dose"])
                st.write("Scheduled time:", med["time"])
                status = medication_status(med)
                st.write("Status:", status)

                if not med["taken"]:
                    if st.button(
                        "Confirm dose taken",
                        key=f"confirm_{med['id']}"
                    ):
                        med["taken"] = True
                        med["confirmed_at"] = current_time()
                        st.rerun()
                else:
                    st.success("Dose confirmation recorded")
                    st.write("Confirmation time:", med["confirmed_at"])

    st.divider()
    st.header("📝 Daily Symptom Report")

    with st.form("symptom_report"):
        pain = st.slider("Pain level (0 = none, 10 = severe)", 0, 10, 0)

        nausea = st.selectbox(
            "Nausea level",
            ["None", "Mild", "Moderate", "Severe"]
        )

        timing = st.radio(
            "When did symptoms occur?",
            ["Before medication", "After medication", "Not related to medication"],
            horizontal=True
        )

        st.subheader("Additional questions from the doctor")
        answers = {}

        for i, question in enumerate(st.session_state.questions):
            label = question["question"]

            if question["type"] == "Yes/No":
                answers[label] = st.radio(
                    label,
                    ["No", "Yes", "Unsure"],
                    key=f"symptom_q_{i}",
                    horizontal=True
                )
            else:
                answers[label] = st.text_area(
                    label,
                    key=f"symptom_text_{i}"
                )

        notes = st.text_area("Other symptoms or notes")
        save_report = st.form_submit_button("Save symptom report")

    if save_report:
        st.session_state.symptoms.append({
            "Date": date.today().isoformat(),
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Patient ID": st.session_state.patient_id,
            "Pain level": pain,
            "Nausea": nausea,
            "Symptom timing": timing,
            "Doctor questions": answers,
            "Other notes": notes
        })
        st.success("Symptom report saved.")
        st.rerun()

# ==================================================
# DOCTOR DASHBOARD
# ==================================================
elif page == "Doctor Dashboard":
    st.header("🩺 Doctor Dashboard")
    st.caption("Review the demo patient's medication and symptom records.")

    st.subheader("➕ Add a prescribed medication")

    with st.form("add_medication"):
        med_name = st.text_input("Medication name")
        dose = st.text_input("Prescribed dose")
        scheduled_time = st.time_input(
            "Daily scheduled time",
            value=datetime.strptime("09:00", "%H:%M").time()
        )
        add_med = st.form_submit_button("Add medication")

    if add_med:
        if med_name.strip() and dose.strip():
            st.session_state.medications.append({
                "id": st.session_state.next_med_id,
                "name": med_name.strip(),
                "dose": dose.strip(),
                "time": scheduled_time.strftime("%H:%M"),
                "taken": False,
                "confirmed_at": None
            })
            st.session_state.next_med_id += 1
            st.success("Medication added to the demo schedule.")
            st.rerun()
        else:
            st.error("Enter both the medication name and dose.")

    st.divider()
    st.subheader("📋 Current medication schedule")

    if st.session_state.medications:
        medication_rows = []
        for med in st.session_state.medications:
            medication_rows.append({
                "Medication": med["name"],
                "Dose": med["dose"],
                "Scheduled time": med["time"],
                "Status": medication_status(med),
                "Confirmed at": med["confirmed_at"] or "—"
            })

        st.dataframe(medication_rows, use_container_width=True)

        if st.button("Clear all demo medications"):
            st.session_state.medications = []
            st.rerun()
    else:
        st.info("No medications added yet.")

    st.divider()
    st.subheader("⚙️ Customize symptom questions")

    with st.form("add_question"):
        new_question = st.text_input("Question to ask the patient")
        question_type = st.selectbox(
            "Answer type",
            ["Yes/No", "Text"]
        )
        add_question = st.form_submit_button("Add question")

    if add_question:
        if new_question.strip():
            st.session_state.questions.append({
                "question": new_question.strip(),
                "type": question_type
            })
            st.success("Question added.")
            st.rerun()
        else:
            st.error("Write a question first.")

    if st.session_state.questions:
        for i, question in enumerate(st.session_state.questions):
            col1, col2 = st.columns([4, 1])
            col1.write(f"**{i + 1}.** {question['question']} ({question['type']})")
            if col2.button("Remove", key=f"remove_question_{i}"):
                st.session_state.questions.pop(i)
                st.rerun()

    st.divider()
    st.subheader("📈 Patient symptom trends")

    reports = st.session_state.symptoms

    if reports:
        st.dataframe(reports, use_container_width=True)

        st.line_chart({
            "Pain level": [report["Pain level"] for report in reports]
        })

        st.subheader("Latest symptom report")
        latest = reports[-1]
        st.write("Patient ID:", latest["Patient ID"])
        st.write("Reported:", latest["Date"], latest["Time"])
        st.write("Pain level:", latest["Pain level"])
        st.write("Nausea:", latest["Nausea"])
        st.write("Symptom timing:", latest["Symptom timing"])
        st.write("Answers to doctor questions:", latest["Doctor questions"])
        st.write("Other notes:", latest["Other notes"])
    else:
        st.info("No symptom reports have been submitted yet.")

st.divider()
st.caption(
    "Limitations: data is temporary and session-based. "
    "There are no separate authenticated accounts, persistent database, "
    "cross-user synchronization, or real push notifications in this version. "
    "Dose confirmations are self-reported."
)
