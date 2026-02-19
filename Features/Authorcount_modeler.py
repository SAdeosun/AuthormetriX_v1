import streamlit as st
import pandas as pd
import plotly.express as px

st.image("images_and_videos/authorcount1.jpg")
st.markdown("**Citation**  \n**Adeosun SO.** *AuthormetriX: Automated Calculation of Individual Authors’ Non-Inflationary Credit-Allocation Schemas’ and Collaboration Metrics from a Scopus Corpus.* **bioRxiv** 2025.01.19.633820; doi: https://doi.org/10.1101/2025.01.19.633820")

st.markdown("**Authorcount modeler function**")
st.write ("""
          - Models credit allocation for two **different** total number of authors (author count), using a specified schema.
          """)
st.markdown("""<hr style="height:4px;border:none;color:#fe8100;background-color:#fe8100;" />""", unsafe_allow_html=True)
st.markdown(" Select credit-allocation schema and specify two ***different*** total number of authors (author counts)")
col1, col2, col3= st.columns([3,1,1], gap="small")

schema = col1.selectbox("Credit-allocation schema", [
   'fractional_equal', 'fractional_LAE', 'fractional_FAE', 'fractional_FLAE', 
   'arithmetic_standard', 'arithmetic_V', 'golden_share','geometric_standard', 'geometric_adaptive', 
   'harmonic_standard', 'harmonic_FLAE','harmonic_parabolic', 'harmonic_LAB'
   ])
n1 = col2.number_input("Author count 1", min_value=2, max_value=50, value=2)
n2 = col3.number_input("Author count 2", min_value=2, max_value=50, value=2)
st.markdown("""<hr style="height:4px;border:none;color:#fe8100;background-color:#fe8100;" />""", unsafe_allow_html=True)




#schemas formulas
#Schema 1.1
def calculate_fractional_equal (n):
  authors = [ i+1 for i in range (n)]
  credits = [1/n for i in range(n)]
  return pd.DataFrame ({'author': authors, f'authorcount_{n}': credits})

#Schema 1.2  Fractional with Last author emphasis (LAE), then equal credits for all preceding authors. 

def calculate_fractional_LAE (n):
  authors = [ i+1 for i in range (n)]
  last_LAE = 0.5
  other_LAE = [(0.5)/(n-1) for _ in range(n-1)]
  credits = other_LAE + [last_LAE]
  return pd.DataFrame ({'author': authors, f'authorcount_{n}': credits})

#Schema 1.3  Fractional with first author emphasis (FAE), then equal credits thereafter. 

def calculate_fractional_FAE (n):
  authors = [ i+1 for i in range (n)]
  first_FAE = 0.5
  other_FAE = [(0.5)/(n-1) for _ in range(n-1)]
  credits = [first_FAE] + other_FAE
  return pd.DataFrame ({'author': authors, f'authorcount_{n}': credits})

#Schema 2.3  First and last authors emphasis (FLAE) then equal credits thereafter; first and last author get at least 0.4 credits
#This is exactly consistent with Credit13_Abramo et al 2013 from Xu et al., 2016
def calculate_fractional_FLAE (n):
  authors = [ i+1 for i in range (n)]
  if n == 2:
    first_FLAE = 0.5
    last_FLAE = 0.5
    credits = [first_FLAE] + [last_FLAE]
    return pd.DataFrame ({'author': authors, f'authorcount_{n}': credits})
  elif n > 2:
    first_FLAE = 0.4
    last_FLAE = 0.4
    other_FLAE = [(0.2)/(n-2) for _ in range(n-2)]
    credits = [first_FLAE] + other_FLAE + [last_FLAE]
    return pd.DataFrame ({'author': authors, f'authorcount_{n}': credits})
  

#Schema 2  Proportional/arithmetic credit alocation: Credit03_proportional schema in Xu et al., 2016 [arithmetic in Liu and Fang 2023]
def calculate_arithmetic(n):
  authors = [ i+1 for i in range (n)]
  credits_arithmetic = [(2 * (1-((i + 1)/(n+1))))/n for i in range(n)]
  credits = credits_arithmetic
  return pd.DataFrame ({'author': authors, f'authorcount_{n}': credits})

#Schema 3.1  Geometric credit alocation: Credit05_Geometric schema in Xu et al., 2016. The ratio of author i to i+1 is constant down the rank, and remains 2 regardless of total number of authors
def calculate_geometric(n):
  authors = [ i+1 for i in range (n)]
  credits_geometric = [(2 ** (n-(i+1)))/((2**n) - 1) for i in range(n)]
  credits = credits_geometric
  return pd.DataFrame ({'author': authors, f'authorcount_{n}': credits})

#Schema 3.2  Geometric credit alocation with an adaptive component: Liu and Fang, 2023 [the ratio of author i to i+1 is same down the rank but decreases with increasing total number of authors]
#Removed "if n = 1"
def calculate_geometric_adaptive(n):
  authors = [ i+1 for i in range (n)]
  adaptive_denominator = (n**(n/(n-1)))-1
  credits_geometric_a = [(n**(1/(n-1))-1)*n**((n-(i+1))/(n-1))/adaptive_denominator for i in range(n)]
  credits = credits_geometric_a
  return pd.DataFrame ({'author': authors, f'authorcount_{n}': credits})

#Schema 4.1  Harmonic credit alocation based on the standard schema
def calculate_harmonic_standard(n):
  authors = [ i+1 for i in range (n)]
  credits_std = [1 / (i + 1) for i in range(n)] #numerator in formula, i.e 1/r for each position
  total_credits_std = sum(credits_std) # sum of all reciprocals of each position, i.e 1/1 + 1/2 + 1/3 +...1/N, The nature of this formula needs "normalization"
  normalized_credits_std = [credit / total_credits_std for credit in credits_std]
  credits = normalized_credits_std
  return pd.DataFrame ({'author': authors, f'authorcount_{n}': credits})

#Schema 4.2 TRUE Harmonic parabolic credit alocation based on the correct formula for the harmonic parabolic schema that I came up with since Sundlin 2023 is neither harmonic nor parabolic.
def calculate_harmonic_parabolic(n):
    authors = [ i+1 for i in range (n)]
    symetrical_harmonic_credits = [1 / min((i + 1), (n+1-(i+1))) for i in range(n)] #I intentionaly did not further simplify the formula 
    #but kept the standard python i+1 in the second expression inside the min() method; it could have been (n-i)
    total_symetrical_harmonic_credits = sum(symetrical_harmonic_credits) # sum of all credits; needed for normalization to 1
    normalized_credits_par = [credit / total_symetrical_harmonic_credits for credit in symetrical_harmonic_credits]
    credits = normalized_credits_par
    return pd.DataFrame ({'author': authors, f'authorcount_{n}': credits})

#Called Arithmetic_V because this formular (originally from Aziz and Rozing, 2013) named harmonic parabolic by Sundling, 2023 turns out to be neither harmonic nor parabolic.
def calculate_arithmetic_V(n):
    authors = [ i+1 for i in range (n)]
    # Calculate the harmonic series for the middle authors
    h_par_denominator_even = (0.5*(n**2)) + (n)
    h_par_denominator_odd = (0.5*(n**2)) + (n*(1-(1/(2*n))))
    if n % 2 == 0:
      normalized_credits_par = [(1 + abs(n+1-(2*(i+1))))/h_par_denominator_even for i in range (n)]
    else:
      normalized_credits_par = [(1 + abs(n+1-(2*(i+1))))/h_par_denominator_odd for i in range (n)]
    credits = normalized_credits_par
    return pd.DataFrame ({'author': authors, f'authorcount_{n}': credits})


#Schema 4.3 Harmonic credit alocation with first and last author emphasis.
#This is different from parabolic which is symmetric around the middle; here, first and last authors get more credits than in harmonic_parabolic
#Removed "if n = 1"
def calculate_harmonic_FLAE(n):
    authors = [ i+1 for i in range (n)]
    FLAE_credits = [1 / (i + 1) for i in range(n)]
    FLAE_denominator = sum(FLAE_credits)
    first_FLAE = [1.5/(2*FLAE_denominator)]
    last_FLAE = [1.5/(2*FLAE_denominator)]
    middle_FLAE = [(1 / (i + 2))/FLAE_denominator for i in range(1, n - 1)]
    all_normalized_credits_FLAE = first_FLAE + middle_FLAE + last_FLAE
    credits = all_normalized_credits_FLAE
    return pd.DataFrame ({'author': authors, f'authorcount_{n}': credits})



#Schema 4.4  Golden share credit alocation (this one gives the highest credit proportion [0.62] to the first author. Assimakis & Adam 2010 eq #28; 
# another simpler formula (which I initially used) is available in Xu et al., J. Infor Sci. 2022 eq#11)

def calculate_golden_share(n):
  if n == 1:
    return pd.DataFrame ({'author': [1], f'authorcount_{n}': [1]})
  elif n > 1:
    authors = [ i+1 for i in range (n)]
    credits_gold = [0.618**(2*(i+1)-1) for i in range(n-1)]
    credits_gold_last = [0.618**(2*(n)-2)]
    credits = credits_gold + credits_gold_last
    return pd.DataFrame ({'author': authors, f'authorcount_{n}': credits})


#Harmonic_LAB
def calculate_harmonic_LAB(n):
    if n == 1:
      return pd.DataFrame ({'author': [1], f'authorcount_{n}': [1.0]})
    elif n == 2:
      return pd.DataFrame ({'author': [1, 2], f'authorcount_{n}': [0.5659, 0.4341]})
    authors = [ i+1 for i in range (n)]
    credits_LAB = [1 / i  for i in range(1, n)]
    penultimate = credits_LAB[-1]
    last_author_credit = penultimate * (((n-2)*0.5226)+0.5643)
    credits_LAB.append(last_author_credit)
    total_credits_LAB = sum(credits_LAB)
    normalized_credits_LAB = [cred / total_credits_LAB for cred in credits_LAB]
    credits = normalized_credits_LAB
    return pd.DataFrame ({'author': authors, f'authorcount_{n}': credits})


#calculating credits for selected specified authorcount 1, based on selected schema
if schema == 'fractional_equal':
  df1 = calculate_fractional_equal(n1)
elif schema == 'fractional_LAE':
  df1 = calculate_fractional_LAE(n1)
elif schema == 'fractional_FAE':
  df1 = calculate_fractional_FAE(n1)
elif schema == 'fractional_FLAE':
  df1 = calculate_fractional_FLAE(n1)
elif schema == 'arithmetic_standard':
  df1 = calculate_arithmetic(n1)
elif schema == 'arithmetic_V':
  df1 = calculate_arithmetic_V(n1) 
elif schema == 'geometric_standard':
  df1 = calculate_geometric(n1)
elif schema == 'geometric_adaptive':
  df1 = calculate_geometric_adaptive(n1)
elif schema == 'harmonic_standard': 
  df1 = calculate_harmonic_standard(n1)
elif schema == 'harmonic_parabolic':
  df1 = calculate_harmonic_parabolic(n1)
elif schema == 'harmonic_FLAE':
  df1 = calculate_harmonic_FLAE(n1)
elif schema == 'golden_share':
  df1 = calculate_golden_share(n1)
elif schema == 'harmonic_LAB':
  df1 = calculate_harmonic_LAB(n1)



#calculating credits for selected specified authorcount 2, based on selected schema 
if schema == 'fractional_equal':
  df2 = calculate_fractional_equal(n2)
elif schema == 'fractional_LAE':
  df2 = calculate_fractional_LAE(n2)
elif schema == 'fractional_FAE':
  df2 = calculate_fractional_FAE(n2)
elif schema == 'fractional_FLAE':
  df2 = calculate_fractional_FLAE(n2)   
elif schema == 'arithmetic_standard':
  df2 = calculate_arithmetic(n2)
elif schema == 'arithmetic_V':
  df2 = calculate_arithmetic_V(n2) 
elif schema == 'geometric_standard':
  df2 = calculate_geometric(n2)
elif schema == 'geometric_adaptive':
  df2 = calculate_geometric_adaptive(n2)
elif schema == 'harmonic_standard': 
  df2 = calculate_harmonic_standard(n2)
elif schema == 'harmonic_parabolic':
  df2 = calculate_harmonic_parabolic(n2)
elif schema == 'harmonic_FLAE':
  df2 = calculate_harmonic_FLAE(n2)
elif schema == 'golden_share':
  df2 = calculate_golden_share(n2)
elif schema == 'harmonic_LAB':
  df2 = calculate_harmonic_LAB(n2)


if n1 == n2:
    st.markdown('##### <font color="#FE8100">WARNING</font>: Please select different author counts.', unsafe_allow_html=True)
else:
    merged_df = pd.merge(df1, df2, on='author',how='outer')
    show_table = st.toggle("Show credit-allocation data table")
    if show_table:
        st.markdown(f'#####  Credit-allocation Data Table with {schema} schema')
        pd.options.display.float_format = '{:.8f}'.format #This doesnt help yet
        st.write(merged_df)
    #TABLE NEEDS FIXING; SEEMS TO BE TO THE MAX OF 4 DECIMAL PLACES; WITH GOLDEN share, AUTHOR COUNT 11 UPWARDS IS SHOWING ZERO 
    melted_merged_df = pd.melt(merged_df, id_vars=['author'], value_vars=[f'authorcount_{n1}', f'authorcount_{n2}'], var_name='authorcount', value_name='Credit_allocated')

    fig = px.line(melted_merged_df, x='author', y='Credit_allocated', color='authorcount', markers = True)
    fig.update_yaxes(title_text = 'Author Credit', tick0=0, dtick=0.1, range=[0,0.7])
    st.markdown("""<hr style="height:4px;border:none;color:#fe8100;background-color:#fe8100;" />""", unsafe_allow_html=True)
    st.markdown(f'##### Credit-allocation Plot for Different Author Counts [{schema} schema]')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""<hr style="height:4px;border:none;color:#fe8100;background-color:#fe8100;" />""", unsafe_allow_html=True)
    st.markdown ("*Thank you for using ***AuthormetriX***.    Kindly remember to cite the publication (full citation above).*",unsafe_allow_html=True)
