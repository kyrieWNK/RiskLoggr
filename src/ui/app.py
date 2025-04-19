import sys
import os
import pandas as pd
import io
from datetime import datetime
import altair as alt # Import altair for visualization
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.data_parser.parser import parse_input
import json
import streamlit as st
from src.models import RiskClassification # Import RiskClassification from models.py
from src.data_parser.parser import parse_input
from src.classification.classifier import classify_incident # Import classify_incident
from src.database.database import initialize_database, save_classification_result, log_download, update_classification_result, get_all_classifications # Import database functions

from src.config.config import settings
# print("DEBUG: API key loaded ->", settings.OPENAI_API_KEY) # Commented out for cleaner output

# Initialize the database when the app starts
initialize_database()

st.markdown("""
    <style>
    /* Center content and reduce padding for minimal layout */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 900px;
        margin: auto;
    }

    /* Style Streamlit buttons */
    .stButton>button {
        border-radius: 8px;
        background-color: #14E956;
        color: black;
        font-weight: bold;
        padding: 0.6rem 1rem;
        font-family: monospace;
    }

    /* Subtle code/terminal look */
    .stTextArea textarea {
        background-color: #1A1D26;
        color: #E5E5E5;
        font-family: monospace;
        border-radius: 6px;
        border: 1px solid #333333;
    }

    /* Markdown headers + spacing */
    h1, h2, h3, h4 {
        font-family: monospace;
        font-weight: 600;
        color: #14E956;
        margin-top: 1.2em;
        margin-bottom: 0.6em;
    }

    /* Remove top-right Streamlit menu */
    header .decoration {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for classifications if not already present
if 'session_classifications' not in st.session_state:
    st.session_state.session_classifications = []
if 'user_identity' not in st.session_state:
    st.session_state.user_identity = 'anonymous' # Default user identity

st.title("RiskLoggr")
st.write("Welcome to RiskLoggr - Classify operational risk incidents using AI.")

# Input methods
input_method = st.radio("Choose input method:", ("Enter Text", "Upload File"))

incident_input = None
is_file_input = False

if input_method == "Enter Text":
    incident_input = st.text_area("Enter Incident Description:", height=200)
elif input_method == "Upload File":
    uploaded_file = st.file_uploader("Upload Incident File:", type=['txt'])
    if uploaded_file is not None:
        # Streamlit file uploader provides a file-like object
        # For simplicity, read content directly here.
        # In a more complex app, you might save and parse the path.
        incident_input = uploaded_file.getvalue().decode("utf-8")
        is_file_input = False # We have the content, not a path

if st.button("Classify Incident"):
    if incident_input:
        # Parse the input (though for text area/simple file read, it's just returning content)
        # This step is more relevant for future complex parsing (e.g., PDF, DOCX)
        parsed_content = parse_input(incident_input, is_file=is_file_input)

        if parsed_content.startswith("Error:"):
            st.error(parsed_content)
        else:
            st.info("Classifying incident...")
            classification_result = classify_incident(parsed_content)

            if classification_result:
                st.markdown("###  Classification Result")

                st.markdown(f"** Basel II Category:** {classification_result.basel_ii_category}")
                st.markdown(f"** Severity Score:** {classification_result.severity_score}")
                st.markdown(f"** Root Cause:** {classification_result.root_cause}")

                st.markdown("**🛡 Control Recommendations:**")
                if isinstance(classification_result.control_recommendations, list):
                    for rec in classification_result.control_recommendations:
                        st.markdown(f"- {rec}")
                else:
                    st.markdown(classification_result.control_recommendations)

                st.markdown("### Risk Profile")
                st.markdown(f"**Inherent Risk:** {classification_result.inherent_risk}")
                st.markdown(f"**Residual Risk:** {classification_result.residual_risk}")
                st.markdown(f"**Likelihood:** {classification_result.likelihood}")
                st.markdown(f"**Impact Type(s):** {', '.join(classification_result.impact_type)}")

                st.markdown("### Framework Mappings")
                if classification_result.framework_tags:
                    for tag in classification_result.framework_tags:
                        st.markdown(f"- {tag}")
                else:
                    st.info("No framework mappings found.")

                # Save the classification result to the database and get the ID
                row_id = save_classification_result(incident_input, classification_result)

                st.markdown("---")
                st.markdown("### Manually Adjust Risk Profile and Framework Mappings")

                # Store classification in session state for editing, including the database ID
                if 'editable_classification' not in st.session_state or st.session_state.editable_classification.get('db_id') != row_id:
                     st.session_state.editable_classification = {
                        "db_id": row_id, # Store the database ID
                        "incident_description": incident_input,
                        "basel_ii_category": classification_result.basel_ii_category,
                        "severity_score": classification_result.severity_score,
                        "root_cause": classification_result.root_cause,
                        "control_recommendations": classification_result.control_recommendations,
                        "framework_tags": classification_result.framework_tags,
                        "inherent_risk": classification_result.inherent_risk,
                        "residual_risk": classification_result.residual_risk,
                        "likelihood": classification_result.likelihood,
                        "impact_type": classification_result.impact_type
                    }

                # Editable widgets for new fields
                # Need to store the classification result ID to update the correct row
                # This will require modifying save_classification_result or querying the DB
                # For now, we'll just display the widgets with current values

                # Using st.session_state to hold editable values
                if 'editable_classification' not in st.session_state or st.session_state.editable_classification['incident_description'] != incident_input:
                     st.session_state.editable_classification = {
                        "incident_description": incident_input,
                        "basel_ii_category": classification_result.basel_ii_category,
                        "severity_score": classification_result.severity_score,
                        "root_cause": classification_result.root_cause,
                        "control_recommendations": classification_result.control_recommendations,
                        "framework_tags": classification_result.framework_tags,
                        "inherent_risk": classification_result.inherent_risk,
                        "residual_risk": classification_result.residual_risk,
                        "likelihood": classification_result.likelihood,
                        "impact_type": classification_result.impact_type
                    }


                st.session_state.editable_classification['inherent_risk'] = st.selectbox(
                    "Inherent Risk:",
                    ["Low", "Medium", "High", "Very High"],
                    index=["Low", "Medium", "High", "Very High"].index(st.session_state.editable_classification['inherent_risk']) if st.session_state.editable_classification['inherent_risk'] in ["Low", "Medium", "High", "Very High"] else 0,
                    key='edit_inherent_risk'
                )

                st.session_state.editable_classification['residual_risk'] = st.selectbox(
                    "Residual Risk:",
                    ["Low", "Medium", "High", "Very High"],
                     index=["Low", "Medium", "High", "Very High"].index(st.session_state.editable_classification['residual_risk']) if st.session_state.editable_classification['residual_risk'] in ["Low", "Medium", "High", "Very High"] else 0,
                    key='edit_residual_risk'
                )

                st.session_state.editable_classification['likelihood'] = st.selectbox(
                    "Likelihood:",
                    ["Rare", "Unlikely", "Possible", "Likely", "Certain"],
                    index=["Rare", "Unlikely", "Possible", "Likely", "Certain"].index(st.session_state.editable_classification['likelihood']) if st.session_state.editable_classification['likelihood'] in ["Rare", "Unlikely", "Possible", "Likely", "Certain"] else 0,
                    key='edit_likelihood'
                )

                impact_options = ["Financial", "Legal", "Reputational", "Operational"]
                st.session_state.editable_classification['impact_type'] = st.multiselect(
                    "Impact Type(s):",
                    impact_options,
                    default=st.session_state.editable_classification['impact_type'],
                    key='edit_impact_type'
                )

                # Editable widget for framework tags (as a multi-select for now, could be more sophisticated)
                # Need to get all possible framework tags or allow free text input
                # For now, let's make it a text area for manual editing of the string representation
                # Or maybe a multi-select with the currently assigned tags? Let's go with multi-select for now.
                # This requires knowing all possible tags, which we don't have easily.
                # Let's make it a text area for now, and the user can manually edit the comma-separated list.
                # This is not ideal, but a starting point. A better approach would involve dynamic tag selection.

                # Convert list of strings to a single string for text area
                framework_tags_str = "\n".join(st.session_state.editable_classification['framework_tags'])

                edited_framework_tags_str = st.text_area(
                    "Framework Tags (Edit comma-separated list):",
                    framework_tags_str,
                    key='edit_framework_tags'
                )

                # Convert back to list of strings on update
                st.session_state.editable_classification['framework_tags'] = [tag.strip() for tag in edited_framework_tags_str.split('\n') if tag.strip()]


                if st.button("Save Manual Adjustments"):
                    if st.session_state.editable_classification and st.session_state.editable_classification.get('db_id') is not None:
                        # Create a RiskClassification object from the edited data
                        updated_classification = RiskClassification(
                            basel_ii_category=st.session_state.editable_classification['basel_ii_category'],
                            severity_score=st.session_state.editable_classification['severity_score'],
                            root_cause=st.session_state.editable_classification['root_cause'],
                            control_recommendations=st.session_state.editable_classification['control_recommendations'],
                            framework_tags=st.session_state.editable_classification['framework_tags'],
                            inherent_risk=st.session_state.editable_classification['inherent_risk'],
                            residual_risk=st.session_state.editable_classification['residual_risk'],
                            likelihood=st.session_state.editable_classification['likelihood'],
                            impact_type=st.session_state.editable_classification['impact_type']
                        )
                        # Update the database record
                        update_classification_result(st.session_state.editable_classification['db_id'], updated_classification)
                        st.success("Manual adjustments saved to database.")

                        # Optionally, update the session_classifications list to reflect the changes
                        # This requires finding the entry by ID and updating it.
                        # For simplicity now, we'll just show the success message.
                        # A more robust solution would refetch data or update the specific entry.

                    else:
                        st.warning("No classification result available to save adjustments.")

                # Store classification in session state (this part might need adjustment
                # if we want the session state to reflect manual edits immediately without refetching)
                # For now, keeping it as is, it stores the initial classification result.
                session_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "incident_description": incident_input,
                    "basel_ii_category": classification_result.basel_ii_category,
                    "severity_score": classification_result.severity_score,
                    "root_cause": classification_result.root_cause,
                    "control_recommendations": classification_result.control_recommendations,
                    "framework_tags": ", ".join(classification_result.framework_tags), # Join tags for CSV
                    "inherent_risk": classification_result.inherent_risk,
                    "residual_risk": classification_result.residual_risk,
                    "likelihood": classification_result.likelihood,
                    "impact_type": ", ".join(classification_result.impact_type) # Join impacts for CSV
                }
                st.session_state.session_classifications.append(session_entry)


                # Add a text area for easy copy-paste
                classification_text = f"""
                Basel II Category: {classification_result.basel_ii_category}
                Severity Score: {classification_result.severity_score}
                Root Cause: {classification_result.root_cause}
                Control Recommendations: {classification_result.control_recommendations}
                """
                st.text_area("Copy Classification Result:", classification_text, height=200)

            else:
                st.error("Failed to classify incident. Check API key and logs.")
    else:
        st.warning("Please enter an incident description or upload a file.")

st.markdown("---")
st.markdown("### Session Classifications")

if st.session_state.session_classifications:
    session_df = pd.DataFrame(st.session_state.session_classifications)
    st.dataframe(session_df)

    # Create a CSV from the session data
    csv_buffer = io.StringIO()
    session_df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode('utf-8')

    st.download_button(
        label="Download Session Classifications as CSV",
        data=csv_bytes,
        file_name="session_classifications.csv",
        mime="text/csv",
        on_click=log_download,
        args=("session_csv", st.session_state.user_identity) # Log the download event
    )
else:
    st.info("No classifications in the current session yet.")

st.markdown("---")
st.markdown("### Risk Heatmap (Likelihood vs. Impact)")

# Fetch all classifications from the database
all_classifications_db = get_all_classifications()

if all_classifications_db:
    # Convert to pandas DataFrame
    all_classifications_df = pd.DataFrame(all_classifications_db)

    # Map likelihood and impact to numerical scales
    likelihood_map = {"Rare": 1, "Unlikely": 2, "Possible": 3, "Likely": 4, "Certain": 5}
    impact_map = {"Financial": 1, "Legal": 2, "Reputational": 3, "Operational": 4} # Simplified mapping for heatmap

    # Process impact_type (which is stored as a JSON string list)
    # Expand rows for multiple impact types
    heatmap_data = []
    for index, row in all_classifications_df.iterrows():
        impact_types = json.loads(row['impact_type']) if row['impact_type'] else []
        for impact in impact_types:
            if impact in impact_map:
                heatmap_data.append({
                    'likelihood': row['likelihood'],
                    'impact_type': impact,
                    'likelihood_score': likelihood_map.get(row['likelihood'], 0),
                    'impact_score': impact_map.get(impact, 0),
                    'incident_description': row['incident_description'] # Include description for tooltip
                })

    heatmap_df = pd.DataFrame(heatmap_data)

    if not heatmap_df.empty:
        # Create the heatmap using Altair
        chart = alt.Chart(heatmap_df).mark_circle().encode(
            x=alt.X('likelihood_score:O', title='Likelihood', axis=alt.Axis(values=list(likelihood_map.values()), labelExpr="['Rare', 'Unlikely', 'Possible', 'Likely', 'Certain'][datum.value - 1]")),
            y=alt.Y('impact_score:O', title='Impact Type', axis=alt.Axis(values=list(impact_map.values()), labelExpr="['Financial', 'Legal', 'Reputational', 'Operational'][datum.value - 1]")),
            size='count()', # Size of circles based on count of incidents
            color=alt.Color('count()', legend=alt.Legend(title="Number of Incidents")),
            tooltip=['likelihood', 'impact_type', 'incident_description', 'count()']
        ).properties(
            title='Risk Heatmap'
        ).interactive() # Enable zooming and panning

        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No data available to generate heatmap.")

st.markdown("---")
st.markdown("### Import Legacy Classifications (CSV)")

uploaded_csv_file = st.file_uploader("Upload Legacy Classifications CSV:", type=['csv'])

if uploaded_csv_file is not None:
    try:
        # Read the CSV file into a pandas DataFrame
        legacy_df = pd.read_csv(uploaded_csv_file)

        # Validate expected columns
        required_columns = ['incident_description', 'basel_ii_category', 'severity_score', 'root_cause', 'control_recommendations']
        if not all(col in legacy_df.columns for col in required_columns):
            st.error(f"CSV must contain the following columns: {', '.join(required_columns)}")
        else:
            st.info(f"Found {len(legacy_df)} rows in the uploaded CSV. Importing...")

            # Iterate through rows and save to database
            imported_count = 0
            for index, row in legacy_df.iterrows():
                try:
                    # Create a dummy RiskClassification object from the row data
                    # This assumes the column names match the RiskClassification attributes
                    dummy_classification = RiskClassification(
                        basel_ii_category=row['basel_ii_category'],
                        severity_score=int(row['severity_score']), # Ensure severity score is integer
                        root_cause=row['root_cause'],
                        control_recommendations=row['control_recommendations']
                    )
                    save_classification_result(row['incident_description'], dummy_classification)
                    imported_count += 1
                except Exception as e:
                    st.warning(f"Skipping row {index} due to error: {e}")
                    # Optionally log this error more formally

            st.success(f"Successfully imported {imported_count} classifications from the CSV.")

    except Exception as e:
        st.error(f"Error processing CSV file: {e}")

st.markdown("---")
st.write("user management or API access will probably be integrated here.")