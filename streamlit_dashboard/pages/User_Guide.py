import streamlit as st


st.header('Navigating Your Way to Home Bliss')

st.markdown("""
Welcome to TravelEase Dwellings, your go-to solution for finding 
the most convenient location to stay when looking for a new home. 
\n
Designed as a valuable complement to the [Property Guru](https://www.propertyguru.com.sg/), 
this application aims to streamline the process of discovering an ideal 
living space by considering your daily routines and minimizing travel time 
to frequently visited locations.
\n
In the following sections, we'll guide you through the steps of using the application,
from inputting your frequent locations to discovering the ideal living space and 
exploring nearby properties listed on Property Guru. 
Let's get started on your journey to finding the perfect home tailored to your lifestyle!

---
""")


st.header('User Guide')

st.subheader('Choosing Frequently Visited Places')

st.markdown('''
###### Step 1: Pick Your Spot on the Map

Click on the map to choose a place you frequent.
Look for the red marker—it shows where you've chosen.
            
###### Step 2: Give It a Name (Optional)

Want to make it personal? Enter a name for your spot, like "Tom’s Workplace" or "Sam’s Preschool."

###### Step 3: Choose Your Ride

Select how you usually get there: Drive, Public Transport, or Walk.

###### Step 4: Tell Us How Often

How many times a week do you visit? Let us know!

###### Step 5: Add to Your List

Hit the "Add to Frequently Visited Places" button.
Look for the green marker—it's now in your list!

###### Step 6: See Your Entries

Your added places will appear in a handy table below the map.

###### Step 7: Want to Add More?

Just repeat these simple steps for all your favorite places.
            
###### Step 8:  Ready to Find Your Ideal Location?
            
Once you've added all your frequently visited places, 
click the "Find Ideal Location" button to run the algorithm.
            
---
''')

st.subheader('Exploring Ideal Location and Nearby Properties')

st.markdown('''
###### Step 9: Explore Your Ideal Location

After clicking, a new map will appear below.
Your frequently visited places will be marked in blue, the ideal location in red, and nearby properties in grey.

###### Step 10: Check Property Listings

Click on a grey marker to see property details.
A blue route will outline the travel route to your frequently visited place and property listing information below.

###### Step 11: Refine Your Search with Filters

Utilize filters to tailor your property search:
* Amenities: Find properties that match your desired amenities.
* Property Type: Narrow down your choices based on property types.
* Price: Set a price range to fit your budget.
''')
