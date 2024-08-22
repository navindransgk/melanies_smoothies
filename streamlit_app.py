# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title("My Parents New Healthy Diner")
st.write(
    """Choose the fruits you want in your custom Smoothie
    """
)

name_on_order = st.text_input('Name on Smoothie:')
st.write("The name on your Smoothie will be: ", name_on_order)

#session = get_active_session()
cnx = st.connection("snowflake")
session = cnx.session()

#Loading Fruits from FRUIT_OPTION table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#Convert Snowpark Dataframe to Pandas Dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect(
    'Choose upto 5 ingredients'
    , my_dataframe
    , max_selections = 5
)

if ingredients_list:
    #st.write(ingredients_list)
    #st.text(ingredients_list)

    ingredients_string = ''

    for fruits_chosen in ingredients_list:
        ingredients_string += fruits_chosen + ' '

        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruits_chosen, 'SEARCH_ON'].iloc[0]
        #st.write('The search value for ', fruits_chosen,' is ', search_on, '.')
        
        st.subheader(fruits_chosen + ' Nutrition Information')
        #fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruits_chosen)
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        fruityvice_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    insert_smoothie_fruit_orders = """insert into smoothies.public.orders(ingredients, name_on_order)
    VALUES ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    st.write(insert_smoothie_fruit_orders)
    
    time_to_take_orders = st.button('Submit Order')
    
    if time_to_take_orders:
        session.sql(insert_smoothie_fruit_orders).collect()
        
        st.success('Your Smoothie is ordered!', icon="✅")
