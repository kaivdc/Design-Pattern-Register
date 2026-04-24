import streamlit as st
import os
from utils.registry_utils import RegistryManager, PatternRecord
from utils.template_utils import load_templates
from utils.app_utils import read_pattern_file

if 'manager' not in st.session_state:
    st.session_state.manager = RegistryManager()
if 'templates' not in st.session_state:
    st.session_state.templates = load_templates("templates")
if 'selected_patterns' not in st.session_state:
    st.session_state.selected_patterns = set()

manager = st.session_state.manager
templates = st.session_state.templates

st.sidebar.title("Design Architect v1.0")
nav = st.sidebar.radio("Navigation", ["Pattern Registry", "Template Gallery", "Create New Design Pattern"])

# PAGE 1 - VIEW REGISTRY
if nav == "Pattern Registry":
    st.header("Pattern Registry")

    # Data preparation
    all_categories = sorted(list(set(t.title for t in templates)))
    all_tags = sorted(list(set(tag for p in manager.patterns for tag in p.tags)))

    with st.expander("Filter & Sort Options", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            sort_option = st.selectbox("Sort By:", ["Most Recent", "Alphabetical"])
            category_filter = st.multiselect("Filter by Category:", all_categories)
        with col2:
            tag_filter = st.multiselect("Filter by Tags:", all_tags)
            search_query = st.text_input("Search Title:")

    # Filtering Logic-
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

    # Selection Logic
    has_selection = len(st.session_state.selected_patterns) > 0

    # Rendering Operations
    with col3:
        st.button(label="Clear All Records", on_click=manager.empty_registry, type="primary")

        if st.button(label="Delete Selected Records", type="primary", disabled=not has_selection):
            manager.delete_multiple_patterns(list(st.session_state.selected_patterns))
            st.session_state.selected_patterns = set()
            st.rerun()

        # Prepare ZIP data only if needed
        bulk_zip_data = manager.get_multiple_patterns_zip(
            list(st.session_state.selected_patterns)) if has_selection else b""

        st.download_button(
            label="Download Selected (.zip)",
            data=bulk_zip_data,
            file_name="bulk_design_patterns.zip",
            mime="application/zip",
            key="bulk_download_btn",
            disabled=not has_selection
        )

    # List Rendering
    st.markdown(f"**Showing {len(filtered_list)} patterns**")

    if not filtered_list:
        st.info("No patterns match your current filters.")
    else:
        for p in filtered_list:
            p_id = p.record_id

            check_col, expander_col, delete_col, download_col = st.columns([1, 20, 2, 2])

            with check_col:
                is_checked = p_id in st.session_state.selected_patterns

                def toggle_select(pid=p_id):
                    if st.session_state[f"select_{pid}"]:
                        st.session_state.selected_patterns.add(pid)
                    else:
                        st.session_state.selected_patterns.discard(pid)


                st.checkbox(
                    "",
                    value=is_checked,
                    key=f"select_{p_id}",
                    on_change=toggle_select,
                    label_visibility="collapsed"
                )

            with expander_col:
                with st.expander(f"{p.title}"):
                    # ... [Keep your existing expander rendering code here] ...
                    st.write(f"**Tags:** {', '.join(p.tags)}")
                    st.caption(f"Path: {p.filepath}")

            with delete_col:
                st.button("🗑️", key=f"del_{p_id}", on_click=manager.delete_pattern, args=(p_id,), type="primary")

            with download_col:
                z_data = manager.get_pattern_zip(p_id)
                if z_data:
                    st.download_button("⬇️", data=z_data, file_name=f"{p.title}.zip", key=f"dl_{p_id}")

# PAGE 2 - VIEW TEMPLATES
elif nav == "Template Gallery":
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