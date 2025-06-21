import streamlit as st
import json
import os

DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            f.write("{}")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    st.title("Miniatures Progress Manager (Web)")

    data = load_data()

    # Sidebar: Army selection/creation
    st.sidebar.header("Army Selection")
    armies = list(data.keys())
    army_choice = st.sidebar.selectbox("Select an existing army or create new", ["-- New Army --"] + armies)

    if army_choice == "-- New Army --":
        new_army_name = st.sidebar.text_input("Enter new army name")
        if new_army_name:
            if new_army_name in data:
                st.sidebar.error("Army already exists.")
                current_army = None
            else:
                current_army = new_army_name
                data[current_army] = {}
                save_data(data)
                st.sidebar.success(f"Army '{current_army}' created.")
        else:
            current_army = None
    else:
        current_army = army_choice

    if current_army is None:
        st.info("Please select or create an army to continue.")
        return

    st.header(f"Army: {current_army}")

    # Input new or update unit
    with st.form("unit_form"):
        miniatures_type = st.text_input("Miniatures type")
        group_name = st.text_input("Group name")
        miniatures_number = st.text_input("Miniatures number")
        rare = st.radio("Rare", ["No", "Yes"], horizontal=True)
        note = st.text_area("Note / Reminder", height=80)
        submitted = st.form_submit_button("Upload / Update unit")

        if submitted:
            if not miniatures_type.strip() or not group_name.strip() or not miniatures_number.strip():
                st.error("Please fill in Miniatures type, Group name and Miniatures number.")
            else:
                try:
                    num = int(miniatures_number)
                    if num < 0:
                        raise ValueError()
                except ValueError:
                    st.error("Miniatures number must be a positive integer.")
                    return

                # Save/update unit
                unit_data = {
                    "miniatures_number": num,
                    "rare": rare,
                    "status": "built",
                    "miniatures_type": miniatures_type.strip(),
                    "note": note.strip()
                }
                data.setdefault(current_army, {})
                data[current_army][group_name.strip()] = unit_data
                save_data(data)
                st.success(f"Unit '{group_name}' saved in army '{current_army}'.")

    st.markdown("---")

    # Display army units
    units = data.get(current_army, {})
    if not units:
        st.info("No units in this army yet.")
    else:
        st.subheader("Units List")
        for unit_name, unit_info in units.items():
            with st.expander(f"{unit_name} ({unit_info['status'].capitalize()})"):
                st.write(f"**Miniatures type:** {unit_info['miniatures_type']}")
                st.write(f"**Number:** {unit_info['miniatures_number']}")
                st.write(f"**Rare:** {unit_info['rare']}")
                st.write(f"**Notes:** {unit_info['note']}")

                # Status update
                status_options = ["built", "work", "painted"]
                new_status = st.selectbox(
                    f"Update status for '{unit_name}'",
                    status_options,
                    index=status_options.index(unit_info.get("status", "built")),
                    key=f"status_{unit_name}"
                )
                if new_status != unit_info.get("status", "built"):
                    unit_info["status"] = new_status
                    save_data(data)
                    st.success(f"Status for '{unit_name}' updated to '{new_status}'.")

                # Delete button
                if st.button(f"Delete unit '{unit_name}'", key=f"delete_{unit_name}"):
                    del data[current_army][unit_name]
                    save_data(data)
                    st.success(f"Unit '{unit_name}' deleted. Please refresh the page to see changes.")

    st.markdown("---")

    # Statistics
    st.subheader("Statistics")
    total_miniatures = 0
    status_counts = {"built": 0, "work": 0, "painted": 0}
    for unit_info in units.values():
        total_miniatures += unit_info.get("miniatures_number", 0)
        status = unit_info.get("status", "built")
        if status in status_counts:
            status_counts[status] += unit_info.get("miniatures_number", 0)

    st.write(f"**Total miniatures:** {total_miniatures}")
    for status, count in status_counts.items():
        st.write(f"**{status.capitalize()}:** {count}")

if __name__ == "__main__":
    main()
