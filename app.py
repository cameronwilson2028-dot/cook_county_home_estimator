from html import escape
import streamlit as st
from predictor import load_model, predict

st.set_page_config(page_title='Cook County Home Estimator',page_icon='🏠',layout='wide')
model=load_model()
EXAMPLE={'township_name':'Palatine','sale_year':2025,'building_sqft':1800,'lot_sqft':7500,'bedrooms':3,'full_baths':2,'half_baths':0,'rooms':7,'year_built':1985,'fireplaces':1,'central_air_code':'Central A/C','garage_size_code':'2 cars','basement_type_code':'Full','basement_finish_code':'Unfinished','exterior_wall_code':'Frame','repair_condition_code':'Average','residence_type_code':'2 Story'}
LABELS={'township_name':'Township','sale_year':'Historical sale year','building_sqft':'Building area (sq ft)','lot_sqft':'Lot area (sq ft)','bedrooms':'Bedrooms','full_baths':'Full bathrooms','half_baths':'Half bathrooms','rooms':'Total rooms (excluding bathrooms)','year_built':'Year built','fireplaces':'Fireplaces','central_air_code':'Central air','garage_size_code':'Garage capacity','basement_type_code':'Basement type','basement_finish_code':'Basement finish','exterior_wall_code':'Exterior walls','repair_condition_code':'Repair condition','residence_type_code':'Home style'}

def money(value):
    return f'${round(value/1000)*1000:,.0f}'

def reset():
    for key,value in EXAMPLE.items():st.session_state[key]=value

for key,value in EXAMPLE.items():
    if key not in st.session_state:st.session_state[key]=value

st.markdown('**COOK COUNTY · HOME ESTIMATOR**')
st.title("Explore a home's price range")
st.write('Enter property details to estimate a sale price and an 80% prediction range.')
st.caption('Cook County, Illinois · Historical price basis, 2022–2025 · BUSA 310')

left,right=st.columns([1.35,1],gap='large')
inputs={}
with left:
    heading,reset_col=st.columns([3,1])
    heading.subheader('Your property')
    reset_col.button('Load example',on_click=reset)
    st.caption('The displayed values begin as an example. Edit them to match the home; the estimate updates automatically.')
    main=st.columns(2)
    for i,key in enumerate(['township_name','sale_year','building_sqft','lot_sqft','bedrooms','full_baths']):
        with main[i%2]:
            if key in model['categories']:
                inputs[key]=st.selectbox(LABELS[key],model['categories'][key],key=key)
            elif key=='sale_year':inputs[key]=st.selectbox(LABELS[key],model['years'],key=key)
            else:
                bounds=model['limits'][key]
                inputs[key]=st.number_input(LABELS[key],min_value=int(bounds['min']),max_value=int(bounds['max']),step=1,key=key)
    with st.expander('Additional property details',expanded=True):
        st.caption('These fields also affect the estimate. Check the example values before using the result.')
        columns=st.columns(2)
        for i,key in enumerate(['half_baths','rooms','year_built','fireplaces','central_air_code','garage_size_code','basement_type_code','basement_finish_code','exterior_wall_code','repair_condition_code','residence_type_code']):
            with columns[i%2]:
                if key in model['categories']:inputs[key]=st.selectbox(LABELS[key],model['categories'][key],key=key)
                else:
                    bounds=model['limits'][key]
                    inputs[key]=st.number_input(LABELS[key],min_value=int(bounds['min']),max_value=int(bounds['max']),step=1,key=key)
    st.caption('No address or personal information required. Entries are sent to the app to calculate your estimate; this app does not save them to a database.')

with right:
    st.subheader('Your estimate')
    try:
        result=predict(model,inputs)
    except ValueError as error:
        st.error(str(error))
    else:
        with st.container(border=True):
            st.metric('Estimated sale price',money(result['estimate']))
            st.caption(f"{inputs['township_name']} · {inputs['sale_year']} price basis")
            st.markdown('#### 80% prediction range')
            st.subheader(f"{money(result['low'])} – {money(result['high'])}")
            marker=100*(result['estimate']-result['low'])/(result['high']-result['low'])
            st.markdown(f'<div aria-hidden="true" style="height:8px;border-radius:6px;background:linear-gradient(90deg,#2458e5,#f9c85c);position:relative;margin:18px 0"><span style="position:absolute;left:{marker:.2f}%;top:-5px;height:18px;width:4px;background:#142d4e"></span></div>',unsafe_allow_html=True)
            st.write('The range targets 80% coverage across similar homes. A particular home can sell outside it.')
        if result['unusual'] or result['estimate']>1_500_000:
            st.warning('Some details or the estimated value are unusual for this sample. Treat this estimate with extra caution.')
        st.info('Historical estimate, not a current appraisal. The model does not measure current 2026 market conditions.')
    st.image('https://upload.wikimedia.org/wikipedia/commons/c/c7/Chicago_bungalow.jpg',caption='Illustrative suburban Chicago bungalow')
    st.caption('Photo: [blahedo / Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Chicago_bungalow.jpg), [CC BY-SA 2.5](https://creativecommons.org/licenses/by-sa/2.5/).')

st.divider()
st.subheader("Measured on homes the model hadn't seen")
m=model['metrics']
for col,(label,value) in zip(st.columns(4),[('Test homes inside the range',f"{m['coverage']:.1%}"),('Test MAE',money(m['mae'])),('Test R²',f"{m['r2']:.3f}"),('Test homes',f"{m['test_n']:,}")]):
    col.metric(label,value)
with st.expander('Data, model and limitations'):
    st.write('The source is a sample of 9,972 qualifying Cook County sales from 2022–2025, not all county sales. One randomly selected sale per property leaves 9,837 unique parcels. The fixed random split uses 60% to train, 20% to calibrate ranges and 20% to test. No property appears in multiple sets.')
    st.write('The model is ordinary least squares on natural log of sale price, with numeric property characteristics and categorical dummy variables. Numeric inputs use training-set standardization. A training-residual smearing adjustment converts predictions to dollars. The separate calibration sample determines the finite-sample 80th-percentile absolute log error, q. The range is [prediction × exp(-q), prediction × exp(q)]. The model is not refit after calibration.')
    st.write('The 80% target is marginal coverage under comparable-data assumptions. It is not a guarantee for an individual house or neighborhood. The random historical test split does not establish future-year forecasting accuracy. Official source records may have been revised after the sale.')
    st.write('This dedicated website regression differs from the earlier notebook split and omits school, crime and walkability inputs. It does not measure a specific street, renovations, or detailed interior condition. High-value homes may be less reliable. The $32.5 million sale was not removed merely for being an outlier.')
    st.markdown('Sources: [Cook County sales](https://datacatalog.cookcountyil.gov/d/wvhk-k5uv), [property characteristics](https://datacatalog.cookcountyil.gov/d/x54s-btds), [parcel geography](https://datacatalog.cookcountyil.gov/d/nj4t-kc8j). [Split-conformal prediction method](https://statgrades.berkeley.edu/~ryantibs/statlearn-s24/lectures/conformal.pdf).')
st.caption('BUSA 310 student research project · Model prepared October 8, 2026')
