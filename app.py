import streamlit as st
import os
from utils.registry_utils import RegistryManager, PatternRecord
from utils.template_utils import load_templates
from utils.app_utils import read_pattern_file

if 'manager' not in st.session_state:
    st.session_state.manager = RegistryManager()
if 'templates' not in st.session_state:
    st.session_state.templates = load_templates("templates")

manager = st.session_state.manager
templates = st.session_state.templates

st.sidebar.title("Design Architect v1.0")
nav = st.sidebar.radio("Navigation", ["View Registry", "View Templates", "Create New Design Pattern"])

# PAGE 1 - VIEW REGISTRY
if nav == "View Registry":
    st.header("Pattern Registry")

    # Autopopulate Categories from Templates
    all_categories = sorted(list(set(t.title for t in templates)))

    # Autopopulate Tags from existing Patterns
    all_tags = set()
    for p in manager.patterns:
        for tag in p.tags:
            all_tags.add(tag)
    all_tags = sorted(list(all_tags))

    with st.expander("Filter & Sort Options", expanded=True):
        col1, col2, col3 = st.columns(3)

        # Sort by column
        with col1:
            sort_option = st.selectbox("Sort By:", ["Most Recent", "Alphabetical"])
            category_filter = st.multiselect("Filter by Category:", all_categories)

        # Filter by column
        with col2:
            tag_filter = st.multiselect("Filter by Tags:", all_tags)
            search_query = st.text_input("Search Title:")

        # Operations column
        with col3:
            clear_option = st.button(label="Clear All Records", on_click=manager.empty_registry, type="primary")


    filtered_list = list(manager.patterns)

    if category_filter:
        filtered_list = [p for p in filtered_list if p.category in category_filter]

    if tag_filter:
        filtered_list = [p for p in filtered_list if any(tag in p.tags for tag in tag_filter)]

    if search_query:
        filtered_list = [p for p in filtered_list if search_query.lower() in p.title.lower()]

    if sort_option == "Alphabetical":
        filtered_list.sort(key=lambda x: x.title.lower())
    else:
        filtered_list.sort(key=lambda x: x.date, reverse=True)

    st.markdown(f"**Showing {len(filtered_list)} patterns**")

    if not filtered_list:
        st.info("No patterns match your current filters.")
    else:
        for p in filtered_list:
            with st.expander(f"[{p.category}] {p.title}"):
                st.write(f"**Tags:** {', '.join(p.tags)}")
                st.write(f"**Created:** {p.date}")

                st.divider()

                # Display the actual file contents
                content = read_pattern_file(p.filepath)

                for line in content.split('\n'):
                    if line.startswith('!['):
                        try:
                            rel_path = line.split('(')[1].split(')')[0]
                            img_abs_path = os.path.abspath(os.path.join("registry", rel_path))

                            if os.path.exists(img_abs_path):
                                st.image(img_abs_path, caption=line.split('[')[1].split(']')[0])
                            else:
                                st.warning(f"Image not found at: {img_abs_path}")
                        except Exception:
                            st.markdown(line)
                    else:
                        st.markdown(line)

                # Provide a path reference at the bottom
                st.caption(f"Path: {p.filepath}")

# PAGE 2 - VIEW TEMPLATES
elif nav == "View Templates":
    st.header("Template Gallery")
    st.write("Browse the underlying structures used to generate the design patterns.")

    if not templates:
        st.warning("No templates loaded. Please check your `templates/` directory.")
    else:
        for t in templates:
            # Use an expander for each template title
            with st.expander(f"{t.title} Template"):
                st.markdown(f"**Category** `{t.title}`")

                # Create a visual representation of the sections
                st.write("### Structure")
                for section in t.sections:
                    # Group sections with a container
                    with st.container(border=True):
                        st.markdown(f"**Section:** {section.name}")

                        # Use a bulleted list for the questions
                        if section.questions:
                            for question in section.questions:
                                question = question.strip('?')
                                question = question.strip('!')
                                st.markdown(f"- {question}")
                        else:
                            st.caption("No questions defined for this section.")

                # Preview blank record
                if st.checkbox("Preview Blank Document Structure", key=f"pre_{t.title}"):
                    preview_lines = [f"# [Title Placeholder]\n", "---"]
                    for section in t.sections:
                        preview_lines.append(f"## {section.name}")
                        for question in section.questions:
                            question = question.strip('?')
                            question = question.strip('!')
                            preview_lines.append(f"### {question}\n")

                    st.code("\n".join(preview_lines), language="markdown")

# PAGE 3 - CREATE NEW DESIGN PATTERN
elif nav == "Create New Design Pattern":
    st.header("Create New Pattern")

    # Selection step
    template_names = [t.title for t in templates]
    selected_name = st.selectbox("Select a Template to use:", template_names)
    selected_template = next(t for t in templates if t.title == selected_name)

    # Prompt user with forms
    with st.form("creation_form"):
        st.info(f"Filling out: {selected_template.title}")
        col1, col2 = st.columns(2)
        u_title = col1.text_input("Pattern Title")
        u_tags = col2.text_input("Tags (comma separated)")

        ui_answers = {}
        for section in selected_template.sections:
            st.markdown(f"### {section.name}")
            for question in section.questions:
                key = f"{section.name}_{question}"
                if question.startswith('!'):
                    label = question.lstrip('!')
                    ui_answers[key] = st.file_uploader(f"Upload: {label}", type=['png', 'jpg', 'jpeg'], key=key, accept_multiple_files=True)
                else:
                    label = question.lstrip('?')
                    ui_answers[key] = st.text_area(label, key=key)

        if st.form_submit_button("Generate Pattern & Save to Registry"):
            if not u_title:
                st.error("Title is required!")
            if not u_tags:
                st.error("Tags are required!")

            else:
                manager.create_design_pattern_from_ui(selected_template, u_title, u_tags, ui_answers)

                # Update registry
                manager.write_registry()

                st.success(f"Successfully created {u_title}!")
                st.balloons()