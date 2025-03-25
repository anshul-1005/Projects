# from datetime import datetime
# start_time = datetime.now()

# #Help
# def proj_chat_tool():
# 	pass


# ###Code

# from platform import python_version
# ver = python_version()

# if ver == "3.8.10":
# 	print("Correct Version Installed")
# else:
# 	print("Please install 3.8.10. Instruction are present in the GitHub Repo/Webmail. Url: https://pastebin.com/nvibxmjw")


# proj_chat_tool()






# #This shall be the last lines of the code.
# end_time = datetime.now()
# print('Duration of Program Execution: {}'.format(end_time - start_time))

##########################################################################################################################################

#Project code
import pandas as pd
import os
from datetime import datetime, timedelta

# Function to process the Excel input
def process_excel(file_path):
    ip_1 = pd.read_excel(file_path, sheet_name="ip_1", skiprows=1)
    ip_1.columns = ['rollno', 'register_sem', 'schedule_sem', 'course_code']
    ip_2 = pd.read_excel(file_path, sheet_name="ip_2", skiprows=1)
    ip_2.columns = ['Date', 'Day', 'Morning', 'Evening']
    ip_3 = pd.read_excel(file_path, sheet_name="ip_3")
    ip_3.columns = ['Room_No', 'Exam_Capacity', 'Block']
    ip_4 = pd.read_excel(file_path, sheet_name="ip_4")
    ip_4.columns = ['Roll', 'Name']
    return ip_1, ip_2, ip_3, ip_4

# Function to calculate dates based on the first Sunday
def assign_dates(ip_2):
    base_date = datetime(2016, 4, 30)  # First Sunday
    days_mapping = {
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6,
        "Sunday": 0,
    }
    ip_2["Date"] = ip_2["Day"].map(lambda day: base_date + timedelta(days=days_mapping[day]))
    return ip_2

# Function to generate seating arrangement and summary
def generate_summary(ip_1, ip_2, ip_3, ip_4, buffer=5, dense=True):
    seating_plan = []

    # Sort rooms by Block (Block 9 first) and then by capacity (larger rooms first)
    ip_3_sorted = ip_3.sort_values(by=['Block', 'Exam_Capacity'], ascending=[True, False])

    for _, exam in ip_2.iterrows():
        date, day = exam["Date"], exam["Day"]
        time_slots = [("Morning", exam["Morning"]), ("Evening", exam["Evening"])]

        for time_slot, courses in time_slots:
            if pd.isna(courses) or courses.strip().upper() == "NO EXAM":
                continue

            course_list = [course.strip() for course in courses.split(";")]
            course_sizes = {}

            # Calculate size of each course and filter students
            remaining_students_by_course = {}
            for course in course_list:
                registered_students = ip_1[ip_1["course_code"] == course]
                if registered_students.empty:
                    continue
                registered_students = registered_students.merge(ip_4, left_on="rollno", right_on="Roll")
                remaining_students_by_course[course] = registered_students
                course_sizes[course] = len(registered_students)

            # Sort courses by size (large to small)
            sorted_courses = sorted(course_sizes.keys(), key=lambda c: course_sizes[c], reverse=True)

            # Allocate students to rooms
            for _, room in ip_3_sorted.iterrows():
                room_no = room["Room_No"]
                room_capacity = room["Exam_Capacity"] - buffer
                if room_capacity <= 0:
                    continue

                allocated_students_in_room = []

                for course in sorted_courses:
                    if course not in remaining_students_by_course:
                        continue

                    students_for_course = remaining_students_by_course[course]
                    if students_for_course.empty or room_capacity <= 0:
                        continue

                    # Adjust allocation count based on dense or sparse mode
                    max_allocation = room_capacity if dense else room_capacity // 2

                    allocate_count = min(len(students_for_course), max_allocation)

                    allocated_students = students_for_course[:allocate_count]
                    remaining_students_by_course[course] = students_for_course[allocate_count:]
                    room_capacity -= allocate_count

                    allocated_students_in_room.append({
                        "course_code": course,
                        "Roll_list": ";".join(allocated_students["rollno"].tolist()),
                        "Allocated_students_count": allocate_count,
                    })

                # If allocation was done in the room, add it to the seating plan
                if allocated_students_in_room:
                    for allocation in allocated_students_in_room:
                        seating_plan.append({
                            "Date": date.strftime("%d/%m/%Y"),
                            "Day": day,
                            "Session": time_slot,
                            "course_code": allocation["course_code"],
                            "Room": room_no,
                            "Allocated_students_count": allocation["Allocated_students_count"],
                            "Roll_list": allocation["Roll_list"],
                        })

    seating_plan_df = pd.DataFrame(seating_plan)
    return seating_plan_df

# Main function
def main(file_path, buffer=5, dense=True, output_file="summary_output.xlsx"):
    ip_1, ip_2, ip_3, ip_4 = process_excel(file_path)

    # Assign dates based on the first Sunday
    ip_2 = assign_dates(ip_2)

    # Generate seating arrangement summary
    summary_df = generate_summary(ip_1, ip_2, ip_3, ip_4, buffer, dense)

    # Save summary to Excel
    summary_df.to_excel(output_file, index=False, columns=[
        "Date", "Day", "course_code", "Room", "Allocated_students_count", "Roll_list"
    ])

    print(f"Summary file saved as: {output_file}")

# File path and execution
file_path = "/content/2024 Python Project Part 1. Group of two.xlsx"
output_file = "/content/summary_output.xlsx"
buffer = 5  # Adjust buffer here (e.g., set to 0 for no buffer)
dense = True  # Set to False for sparse mode
main(file_path, buffer=buffer, dense=dense, output_file=output_file)

#classroom allocation part########################################################################
import pandas as pd
import os

# Function to load and preprocess Excel input sheets
def load_excel_data(file_path):
    sheet1 = pd.read_excel(file_path, sheet_name="ip_1", skiprows=1)
    sheet1.columns = ['rollno', 'register_sem', 'schedule_sem', 'course_code']

    sheet2 = pd.read_excel(file_path, sheet_name="ip_2", skiprows=1)
    sheet2.columns = ['Date', 'Day', 'Morning', 'Evening']

    sheet3 = pd.read_excel(file_path, sheet_name="ip_3")
    sheet3.columns = ['Room_No', 'Exam_Capacity', 'Block']

    sheet4 = pd.read_excel(file_path, sheet_name="ip_4")
    sheet4.columns = ['Roll', 'Name']

    output2 = pd.read_excel(file_path, sheet_name="op_2", skiprows=1)
    output2.columns = ['Room_No', 'Exam_Capacity', 'Block', 'Vacant']

    return sheet1, sheet2, sheet3, sheet4, output2

# Function to create attendance sheets for exams
def create_attendance_files(seating_data, student_info, output_directory):
    os.makedirs(output_directory, exist_ok=True)  # Ensure output folder exists

    for _, row in seating_data.iterrows():
        if pd.isnull(row["Date"]):  # Skip invalid rows
            continue

        # Extract session details
        date_str = pd.to_datetime(row["Date"]).strftime("%d_%m_%Y")
        session_type = row["Session"].lower()
        course = row["course_code"]
        room = row["Room"]
        roll_numbers = row["Roll_list"].split(";")

        # Fetch relevant student details
        filtered_students = student_info[student_info["Roll"].isin(roll_numbers)]

        # Create attendance data with space for signatures
        attendance_sheet = filtered_students.copy()
        attendance_sheet["Sign"] = ""

        # Add blank rows for invigilators/TAs
        blanks = pd.DataFrame([{"Roll": "", "Name": "", "Sign": ""} for _ in range(5)])
        attendance_sheet = pd.concat([attendance_sheet, blanks], ignore_index=True)

        # Save attendance sheet as Excel file
        filename = f"{date_str}_{course}_{room}_{session_type}.xlsx"
        attendance_sheet.to_excel(os.path.join(output_directory, filename), index=False, columns=["Roll", "Name", "Sign"])

# Function to generate the seating arrangement plan
def plan_seating(exam_data, schedule, rooms, students, buffer=5, dense=True):
    seating_arrangements = []
    session_vacancy = {}

    # Sort rooms by priority (Block and Capacity)
    sorted_rooms = rooms.sort_values(by=["Block", "Exam_Capacity"], ascending=[True, False])

    for _, exam_day in schedule.iterrows():
        date = exam_day["Date"]
        day_name = exam_day["Day"]
        sessions = [("Morning", exam_day["Morning"]), ("Evening", exam_day["Evening"])]

        for session_name, course_list in sessions:
            session_key = f"{day_name}_{session_name}"
            room_vacancies = {room: cap - buffer for room, cap in zip(rooms["Room_No"], rooms["Exam_Capacity"])}
            session_vacancy[session_key] = room_vacancies.copy()

            if pd.isnull(course_list) or course_list.strip().upper() == "NO EXAM":
                continue

            courses = [course.strip() for course in course_list.split(";")]
            student_count_by_course = {}

            # Prepare course-wise student data
            remaining_students = {}
            for course in courses:
                course_students = exam_data[exam_data["course_code"] == course]
                if course_students.empty:
                    continue
                merged_data = course_students.merge(students, left_on="rollno", right_on="Roll")
                remaining_students[course] = merged_data
                student_count_by_course[course] = len(merged_data)

            # Allocate students to rooms by course size
            sorted_courses = sorted(student_count_by_course.keys(), key=lambda x: student_count_by_course[x], reverse=True)

            for _, room in sorted_rooms.iterrows():
                room_no = room["Room_No"]
                capacity = room_vacancies.get(room_no, 0)

                if capacity <= 0:
                    continue

                allocations = []

                for course in sorted_courses:
                    if course not in remaining_students:
                        continue

                    student_pool = remaining_students[course]
                    if student_pool.empty or capacity <= 0:
                        continue

                    allocation_limit = capacity if dense else capacity // 2
                    allocation_count = min(len(student_pool), allocation_limit)

                    allocated = student_pool.iloc[:allocation_count]
                    remaining_students[course] = student_pool.iloc[allocation_count:]
                    capacity -= allocation_count

                    allocations.append({
                        "course_code": course,
                        "Roll_list": ";".join(allocated["rollno"].tolist()),
                        "Allocated_students_count": allocation_count,
                    })

                room_vacancies[room_no] = capacity

                for allocation in allocations:
                    seating_arrangements.append({
                        "Date": date,
                        "Day": day_name,
                        "Session": session_name,
                        "course_code": allocation["course_code"],
                        "Room": room_no,
                        "Allocated_students_count": allocation["Allocated_students_count"],
                        "Roll_list": allocation["Roll_list"],
                    })

            session_vacancy[session_key] = room_vacancies.copy()

    return pd.DataFrame(seating_arrangements), session_vacancy

# Main execution function
def run(file_path, buffer=5, dense=True, output_dir="/content/attendance_sheets"):
    # Load input data
    ip1, ip2, ip3, ip4, ip_op2 = load_excel_data(file_path)

    # Generate seating plan and session-wise vacant seats
    seating_plan, session_vacancy_data = plan_seating(ip1, ip2, ip3, ip4, buffer, dense)

    # Save seating plan and vacancy data to Excel
    with pd.ExcelWriter(file_path, mode='a', if_sheet_exists='replace') as writer:
        seating_plan.to_excel(writer, sheet_name="op_1", index=False)

        for session, vacancy in session_vacancy_data.items():
            session_data = ip_op2.copy()
            session_data["Vacant"] = session_data["Room_No"].map(vacancy)
            session_data.to_excel(writer, sheet_name=session, index=False)

    # Generate attendance sheets
    create_attendance_files(seating_plan, ip4, output_dir)

    print(f"Attendance files have been saved in: {output_dir}")

# File and configuration
file_path = "/content/2024 Python Project Part 1. Group of two.xlsx"
run(file_path, buffer=5, dense=True)