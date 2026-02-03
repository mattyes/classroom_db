import streamlit as st
from streamlit_autorefresh import st_autorefresh
from main import (
    initialize_db,
    get_current_day_and_bloc,
    get_open_rooms_table,
    update_bloc_status,
    update_room_info
)


st.set_page_config("Salles de classe vides", layout="wide")
initialize_db()

st.title("Recherche de salles de classe vides")

# ---------- Auto refresh ----------
st_autorefresh(interval=15_000, key="refresh")

# ---------- Current time ----------
day, bloc = get_current_day_and_bloc()
st.caption(f"{day.capitalize()} — Bloc {bloc}")

# ---------- Open rooms table ----------
st.subheader("Salle Ouverte")

df = get_open_rooms_table(day, bloc)

if df.empty:
    st.info("Aucune salle ouverte pour le moment.")
else:
    st.dataframe(df, width='stretch', hide_index=True)

# ---------- Controls ----------
st.divider()
st.header("Mise à jour de la disponibilité")

with st.expander("Mettre à jour le statut de la salle"):
    room = st.text_input("Numéro de salle (3 chiffres)")
    status = st.radio("Statut", ["Ouverte", "Fermée"], horizontal=True)

    if st.button("Enregistrer"):
        update_bloc_status(
            room_number=room,
            day=day,
            bloc_number=bloc,
            status=status.lower(),
            has_printer=None,
            has_computer=None
        )
        st.success("Mis à jour.")

st.divider()
st.header("Mise à jour des informations de la salle")

with st.expander("Mettre à jour les informations de la salle"):
    room = st.text_input("Numéro de salle (3 chiffres)", key="info_room")
    printer = st.selectbox("Imprimante disponible ?", ["Oui", "Non"])
    computer = st.selectbox("Ordinateur disponible ?", ["Oui", "Non"])

    if st.button("Enregistrer les informations"):
        update_room_info(
            room_number=room,
            has_printer=printer,
            has_computer=computer
        )
        st.success("Mis à jour.")