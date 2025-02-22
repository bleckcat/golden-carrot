from datetime import date, datetime
import os
import pdfkit
from flask import Blueprint, request, jsonify, send_file
from bs4 import BeautifulSoup

create_cv = Blueprint('create-cv', __name__)


def calculate_age(birthdate):
    birthdate = datetime.strptime(birthdate, "%Y-%m-%d").date()
    today = date.today()
    age = today.year - birthdate.year - \
        ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age


@create_cv.route('/create-cv', methods=['POST'])
def generate_pdf():
    try:
        html_path = os.path.join(os.path.dirname(
            __file__), f"../mocks/curriculo_{request.json.get('language')}.html")
        with open(html_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

        mappings = {
            "name-input": request.json.get("fullName"),
            "birthdate-input": request.json.get("dateOfBirth"),
            "sex-input": request.json.get("sex"),
            "phone-input": request.json.get("phoneNumber"),
            "address-input": request.json.get("address"),
            "email-input": request.json.get("email"),
            "qtde-deps": request.json.get("childrenCount"),
            "qtde-conj": request.json.get("spouseName"),
            "eng-level-input": request.json.get("englishLevel"),
            "jap-level-input": request.json.get("japaneseLevel"),
            "job-type-input": request.json.get("jobType"),
            "martial-status-input": request.json.get("maritalStatus"),
            "spouse-birth-input": request.json.get("spouseBirthDate"),
            "manequim-size-input": request.json.get("manequimSize"),
            "piercing-tattoo-input": request.json.get("hasTattooOrPiercing"),
            "height-input": request.json.get("height"),
            "weight-input": request.json.get("weight"),
        }

        for field_id, value in mappings.items():
            element = soup.find("td", {"id": field_id})
            if element:
                if isinstance(value, bool):
                    if value:
                        element.string = "X"
                else:
                    element.string = value

        # Add study history
        study_history_table = soup.find("tbody", {"id": "study-history"})
        for study in request.json.get("studyHistory", []):
            row = soup.new_tag("tr")
            at_date = soup.new_tag("td")
            at_date.string = f"{study['startDate']} - {study['endDate']}"
            row.append(at_date)
            university_name = soup.new_tag("td")
            university_name.string = study["universityName"]
            row.append(university_name)
            study_history_table.append(row)

        # Add certifications
        certifications_table = soup.find("tbody", {"id": "certifications"})
        for cert in request.json.get("certifications", []):
            row = soup.new_tag("tr")
            at_date = soup.new_tag("td")
            at_date.string = f"{cert['startDate']} - {cert['endDate']}"
            row.append(at_date)
            certification_name = soup.new_tag("td")
            certification_name.string = cert["certificationName"]
            row.append(certification_name)
            certifications_table.append(row)

        # Add certifications
        health_problems_table = soup.find(
            "tbody", {"id": "health-ploblems-table"})
        for cert in request.json.get("healthProblems", []):
            row = soup.new_tag("tr")
            health_problem_name = soup.new_tag("td")
            health_problem_name.string = cert
            row.append(health_problem_name)
            health_problems_table.append(row)

      # Add work history
        work_history_table = soup.find("tbody", {"id": "work-history"})
        for work in request.json.get("workHistory", []):
            row = soup.new_tag("tr")
            start_end_date = soup.new_tag("td", rowspan="2")
            start_end_date.string = f"{work['startDate']} - {work['endDate']}"
            row.append(start_end_date)
            company_name = soup.new_tag("td")
            company_name.string = work["companyName"]
            row.append(company_name)
            work_history_table.append(row)

            row = soup.new_tag("tr")
            responsibilities = soup.new_tag("td")
            responsibilities.string = work["responsibilities"]
            row.append(responsibilities)
            work_history_table.append(row)

        # Add project history
        project_history_table = soup.find("tbody", {"id": "project-history"})
        for project in request.json.get("projects", []):
            row = soup.new_tag("tr")
            start_end_date = soup.new_tag("td", rowspan="2")
            start_end_date.string = f"{project['startDate']} - {project['endDate']}"
            row.append(start_end_date)
            company_name = soup.new_tag("td")
            company_name.string = project["projectName"]
            row.append(company_name)
            project_history_table.append(row)

            row = soup.new_tag("tr")
            responsibilities = soup.new_tag("td")
            responsibilities.string = project["responsibilities"]
            row.append(responsibilities)
            project_history_table.append(row)

        # Rendering starts here
        temp_html_path = os.path.join(os.path.dirname(
            __file__), "../out/modified_index.html")
        with open(temp_html_path, "w", encoding="utf-8") as file:
            file.write(str(soup))

        pdf_options = {
            "page-size": "A3",
            "margin-top": "10mm",
            "margin-right": "10mm",
            "margin-bottom": "10mm",
            "margin-left": "10mm",
            "enable-local-file-access": ""
        }

        pdf_path = os.path.join(os.path.dirname(__file__), "../out/output.pdf")
        pdfkit.from_file(temp_html_path, pdf_path, options=pdf_options)

        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
