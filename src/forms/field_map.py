"""
Fixed field mapping for the TX Application for Protective Order.
Deliberately hardcoded rather than using Document Intelligence — this is a
single known template. See architecture doc §3.4 for why.
"""

# Maps intake field names to form field identifiers on the official PDF.
# Populate against the actual form's field names once sourced —
# placeholders shown here.
TX_PROTECTIVE_ORDER_FIELD_MAP: dict[str, str] = {
    "petitioner_name": "form_field_petitioner_name",
    "petitioner_address": "form_field_petitioner_address",
    "respondent_name": "form_field_respondent_name",
    "relationship_to_respondent": "form_field_relationship",
    "county": "form_field_county",
    "has_children_with_respondent": "form_field_children_flag",
    "incident_description": "form_field_incident_narrative",
    "case_type": "form_field_case_type",  # family_violence | dating_violence | stalking
}


def fill_form(intake_data: dict, template_path: str, output_path: str) -> str:
    """
    Merge intake_data into the TX form template using
    TX_PROTECTIVE_ORDER_FIELD_MAP, write filled PDF to output_path.
    Returns output_path.
    """
    raise NotImplementedError
