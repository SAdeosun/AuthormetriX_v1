import streamlit as st
import pandas as pd



st.image("images_and_videos/main1.jpg")
st.markdown("**Citation**  \n**Adeosun SO.** *AuthormetriX: Automated Calculation of Individual Authors’ Non-Inflationary Credit-Allocation Schemas’ and Collaboration Metrics from a Scopus Corpus.* **bioRxiv** 2025.01.19.633820; doi: https://doi.org/10.1101/2025.01.19.633820")
st.markdown("**Main function**  \n*Calculates individual authors' metrics (scholarly output metrics based on 15 counting schemas, and scholarly collaboration metrics) when the user supplies a relevant corpus of publications downloaded from Scopus, and a list of authors' Scopus IDs. See the Homepage for how to obtain the needed input information.*")
st.markdown("""<hr style="height:4px;border:none;color:#fe8100;background-color:#fe8100;" />""", unsafe_allow_html=True)

#STEP 1 STARTS
st.markdown ("### STEP 1")
st.markdown ("**Upload the corpus to be analyzed (*Scopus download*), from which authors' metrics will be obtained.**")
raw_corpus = st.file_uploader ("", type = [".csv"])



#Function to preprocess the uploaded corpus file
def corpus_preprocess (df):
  first_corpus = pd.read_csv(df)
  #1.1  Makes sure essential columns do not have empty cells, then renames essential author columns
  corpus01 = first_corpus.dropna(subset = ['Author(s) ID', 'Document Type', 'Year'])
  corpus02 = corpus01.drop_duplicates(subset = ['Author(s) ID', 'Title', 'Source title','Year'])
  corpus03 = corpus02.rename (columns= {'Author(s) ID': 'Authors_ID', 'Document Type': 'Document_Type'})
  corpus = corpus03[['EID', 'Authors', 'Author full names', 'Authors_ID', 'Title', 'Year','Source title', 'Document_Type']].copy()
  #1.2  Converts "Author_ID" with ";" to standard list. Pay close attention to this as it may break the code if Scopus changes their format
  corpus['Authors_ID_list'] = corpus['Authors_ID'].apply(lambda x: [int(ID.strip()) for ID in x.split(';')])
  #1.3  Calculates number of authors
  corpus['authorcount'] = corpus['Authors_ID_list'].apply(len)
  #1.4  Creates a column for the first author ID
  corpus['first_author'] = corpus['Authors_ID_list'].apply(lambda x: x[0])
  #1.5  Creates a column for the last author ID, which applies only to non-single-author publications. Last author is last element of each list
  corpus['last_author'] = corpus['Authors_ID_list'].apply(lambda x: x[-1] if len(x) !=1 else 0) #There was a an abnormal behavior with conversion to integer. 
 

  return corpus, first_corpus



#CORPUS FUNCTION 2: FRACTIONAL CREDIT SCHEMAS
#Adds the 3 types of fractional credit allocation schema to the corpus
def calculate_3_fractional_credit_schemes (corpus):
  #2.1  equal fractional credit
  corpus['fractional_credit_EQ'] = 1/corpus['authorcount']

  #2.2  Last author emphasis (LAE) then equal credits for all preceding authors
  def calculate_fractional_LAE (n):
    if n == 1:
      return [1.0]
    else:
      last_LAE = 0.5
      other_LAE = [(0.5)/(n-1) for _ in range(n-1)]
      return other_LAE + [last_LAE]
  corpus['fractional_credit_LAE'] = corpus['authorcount'].apply(calculate_fractional_LAE)

  #2.3  First author emphasis (FAE) then equal credits thereafter
  def calculate_fractional_FAE (n):
    if n == 1:
      return [1.0]
    else:
      first_FAE = 0.5
      other_FAE = [(0.5)/(n-1) for _ in range(n-1)]
      return [first_FAE] + other_FAE
  corpus['fractional_credit_FAE'] = corpus['authorcount'].apply(calculate_fractional_FAE)

  #2.3  First and last authors emphasis (FLAE) then equal credits thereafter; first and last author get at least 0.4 credits
  #This is exactly consistent with Credit13_Abramo et al 2013 from Xu et al., 2016
  def calculate_fractional_FLAE (n):
    if n == 1:
      return [1.0]
    elif n == 2:
      first_FLAE = 0.5
      last_FLAE = 0.5
      return [first_FLAE] + [last_FLAE]
    elif n > 2:
      first_FLAE = 0.4
      last_FLAE = 0.4
      other_FLAE = [(0.2)/(n-2) for _ in range(n-2)]
      return [first_FLAE] + other_FLAE + [last_FLAE]

  corpus['fractional_credit_FLAE'] = corpus['authorcount'].apply(calculate_fractional_FLAE)

  return corpus

#CORPUS FUNCTION 3 : HARMONIC CREDIT SCHEMAS
#Adds the 3 types of harmonic credit allocation schema to the corpus
def calculate_3_harmonic_credit_schemes (corpus):
  # Function to calculate the harmonic credits according to the order of authors for a given number of authors of an article

  #3.1  Harmonic credit alocation based on the standard schema
  def calculate_harmonic_standard(n):
    credits_std = [1 / (i + 1) for i in range(n)] #numerator in formula, i.e 1/r for each position
    total_credits_std = sum(credits_std) # sum of all reciprocals of each position, i.e 1/1 + 1/2 + 1/3 +...1/N. The nature of this formula needs "normalization"
    normalized_credits_std = [credit / total_credits_std for credit in credits_std]
    return normalized_credits_std

  corpus['harmonic_credit_STD'] = corpus['authorcount'].apply(calculate_harmonic_standard)

  #3.2  TRUE Harmonic parabolic credit alocation based on the correct formula for the harmonic parabolic schema that I came up with since Sundlin 2023 is neither harmonic nor parabolic.
  def calculate_harmonic_parabolic(n):
    symetrical_harmonic_credits = [1 / min((i + 1), (n+1-(i+1))) for i in range(n)] #I intentionaly did not further simplify the formula 
    #but kept the standard python i+1 in the second expression inside the min() method; it could have been (n-i)
    total_symetrical_harmonic_credits = sum(symetrical_harmonic_credits) # sum of all credits; needed for normalization to 1
    normalized_credits_par = [credit / total_symetrical_harmonic_credits for credit in symetrical_harmonic_credits]
    return normalized_credits_par

  corpus['harmonic_credit_PAR'] = corpus['authorcount'].apply(calculate_harmonic_parabolic)

  #Called Arithmetic_V because this formular (originally from Aziz and Rozing, 2013) named harmonic parabolic by Sundling, 2023 turns out to be neither harmonic nor parabolic.
  def calculate_arithmetic_V(n):
    # Calculate the harmonic series for the middle authors
    h_par_denominator_even = (0.5*(n**2)) + (n)
    h_par_denominator_odd = (0.5*(n**2)) + (n*(1-(1/(2*n))))
    if n % 2 == 0:
      normalized_credits_par = [(1 + abs(n+1-(2*(i+1))))/h_par_denominator_even for i in range (n)]
    else:
      normalized_credits_par = [(1 + abs(n+1-(2*(i+1))))/h_par_denominator_odd for i in range (n)]
    return normalized_credits_par
  
  corpus['arithmetic_credit_V'] = corpus['authorcount'].apply(calculate_arithmetic_V)

  #3.3  Harmonic credit alocation with first and last author emphasis.
  #This is different from parabolic which is symmetric around the middle; here, first and last authors get more credits than in harmonic_parabolic. Normalization necessary; makes the formula simpler
 
  def calculate_harmonic_FLAE(n):
      if n == 1:
          return [1.0]
      FLAE_credits = [1 / (i + 1) for i in range(n)]
      FLAE_denominator = sum(FLAE_credits)
      first_FLAE = [1.5/(2*FLAE_denominator)]
      last_FLAE = [1.5/(2*FLAE_denominator)]
      middle_FLAE = [(1 / (i + 2))/FLAE_denominator for i in range(1, n - 1)]
      all_normalized_credits_FLAE = first_FLAE + middle_FLAE + last_FLAE
      return all_normalized_credits_FLAE

  corpus['harmonic_credit_FLAE'] = corpus['authorcount'].apply(calculate_harmonic_FLAE)

  return corpus


#CORPUS FUNCTION 4 : ARITHMETIC AND GEOMETRIC CREDIT SCHEMAS
def calculate_arithmetic_and_geometric_credit_schemes (corpus):
  

  #3.1  Arithmetic credit alocation: Credit03_proportional schema in Xu et al., 2016
  def calculate_arithmetic(n):
    credits_arithmetic = [(2 * (1-((i + 1)/(n+1))))/n for i in range(n)]
    return credits_arithmetic

  corpus['arithmetic_credit'] = corpus['authorcount'].apply(calculate_arithmetic)

  #3.2 Based on the golden number. It somewhat prioritizes the first author (never less than 0.62); Assimakis & Adam 2010 eq #28; 
  # another simpler formula(which I initially used) is available in Xu et al., J. Infor Sci. 2022 eq#11)
  def calculate_golden_share(n):
    if n == 1:
      return [1]
    elif n > 1:
      credits_gold = [0.618**(2*(i+1)-1) for i in range(n-1)]
      credits_gold_last = [0.618**(2*(n)-2)]
      return credits_gold + credits_gold_last

  corpus['golden_share_credit'] = corpus['authorcount'].apply(calculate_golden_share)


  #3.3  Geometric credit alocation: Credit05_Geometric schema in Xu et al., 2016
  def calculate_geometric(n):
    credits_geometric = [(2 ** (n-(i+1)))/((2**n) - 1) for i in range(n)] 
    return credits_geometric
  
  corpus['geometric_credit'] = corpus['authorcount'].apply(calculate_geometric)
 

  #3.4 Geometric with i:i+1 ratio adaptivity (2 in standard geometric regardless of total author number)
  def calculate_geometric_adaptive(n):
    if n == 1:
      return [1.0]
    else:
      adaptive_denominator = (n**(n/(n-1)))-1
      credits_geometric_a = [(n**(1/(n-1))-1)*n**((n-(i+1))/(n-1))/adaptive_denominator for i in range(n)]
      return credits_geometric_a

  corpus['geometric_credit_adaptive'] = corpus['authorcount'].apply(calculate_geometric_adaptive)
  

  return corpus





#SCID FUNCTION 1
def extract_whole_and_straight_counts(corpus, scids_df):
  #S1.1
  #Instruction would have the Scopus IDs to be in the first column; so I rename whatever the first column is to 'scids'
  scids_df = scids_df.rename(columns={scids_df.columns[0]: 'scids'})
  
  #S1.2
  #Extracts whole counts; the number of appearances (authorships) of each scid
  #Flattens the Authors_ID_list, to a single list where scids can appear multiple times and from which we do the count of appearances
  flattened_Authors_ID_list = [item for sublist in corpus['Authors_ID_list'] for item in sublist]
  #The flattened column is converted to a series, value_counts done and index reset, to make it a dataframe that can be left_joined with the original scids_df dataframe
  id_counts = pd.Series(flattened_Authors_ID_list).value_counts().reset_index()
  #names the columns in the id_counts dataframe
  id_counts.columns = ['scids', 'whole_fullcount']
  #left-joins id_counts with scids_df, fill rows for scids that are not found with zeros, and then convert the 'whole_credit_fullcount' column to integers
  scids_df = scids_df.merge(id_counts, on='scids', how='left').fillna(0)
  scids_df['whole_fullcount'] = scids_df['whole_fullcount'].astype(int)

  #S1.3
  #Extract straight credits for first and last authors
  #Initialize counts
  scids_df['straight_firstauthor'] = 0
  scids_df['straight_lastauthor'] = 0
  # Loop through scids
  for scid in scids_df['scids']:
    # Count matches in authorsid.
    first_pubs = (corpus['first_author']== scid).sum()
    last_pubs = (corpus['last_author']== scid).sum()
    # Update columns
    scids_df.loc[scids_df['scids']==scid, 'straight_firstauthor'] += first_pubs
    scids_df.loc[scids_df['scids']==scid, 'straight_lastauthor'] += last_pubs
  return scids_df

def extract_fractional_standard(corpus, scids_df):
    # Explode the author_list column in corpus
    corpus = corpus [['Authors_ID_list', 'fractional_credit_EQ']]
    corpus_exploded = corpus.explode('Authors_ID_list').reset_index(drop=True)

    # Create a dictionary to store the sum of scores for each scid
    score_dict = corpus_exploded.groupby('Authors_ID_list')['fractional_credit_EQ'].sum().to_dict()

    # Create the scid_score column in df2
    scids_df['fractional_equal'] =  scids_df['scids'].apply(lambda x: score_dict.get(x, 0))

    return scids_df



def extract_allocation_sum(corpus, scids_df, allocation_col, sum_col):
    # Create a dictionary in 'corpus' where each author in 'Authors_ID_list' is paired with corresponding value in 'allocation_type1'
    corpus['author_allocation_dict'] = corpus.apply(
        lambda row: dict(zip(row['Authors_ID_list'], row[allocation_col])) if isinstance(row[allocation_col], list) else {}, axis=1
    )

    # Expand the author_allocation_dict to a new DataFrame for easy summation
    author_allocations = pd.DataFrame(
        [(author, alloc) for d in corpus['author_allocation_dict'] for author, alloc in d.items()],
        columns=['scids', sum_col]
    )

    # Group by 'scids' and sum the allocations for each author ID
    allocation_sum = author_allocations.groupby('scids')[sum_col].sum().reset_index()

    # Merge the summed allocations with the original scids_df, filling missing values with 0
    scids_df = scids_df.merge(allocation_sum, on='scids', how='left').fillna({sum_col: 0})

    return scids_df

def Multiplex_extract_allocation_sum(corpus, scids_df, column_pairs):
    for original_col, new_col in column_pairs:
        scids_df = extract_allocation_sum(corpus, scids_df, original_col, new_col)
    return scids_df


#Collaboration Functions
def count_one_author_publications (corpus, scids_df):
  #Filter the corpus to only single-author documents, i.e when authorcount ==1
  corpus_single_author = corpus.query ('authorcount == 1').copy() #the copy was necessary to avoid the 'SettingWithCopyWarning'
  #This step was necessary to avoid using "isin", so each single author was first pulled out as an integer to get a perfect matches
  corpus_single_author['one_author'] = corpus_single_author['Authors_ID_list'].apply(lambda x: x[0])
  #Initialize counts
  scids_df['single_author_publications'] = 0
  # Loop through scids
  for scid in scids_df['scids']:
    one_author_pubs = len(corpus_single_author.query ("one_author == @scid"))
    # Update columns
    scids_df.loc[scids_df['scids']==scid, 'single_author_publications'] += one_author_pubs
  return scids_df



def calculate_collaborations_DC_CI_CC (corpus, scids_df):
  #DC - from scids_df only
  scids_df['degree_of_collaboration'] = ((scids_df['whole_fullcount'] - scids_df['single_author_publications'])/scids_df['whole_fullcount'])#.fillna(0)
  #CI - i.e average NAPD of multi_author publications only (from both dataframes)
  corpus['Authors_ID_list'] = corpus['Authors_ID_list'].apply(lambda x: [int(i) for i in x])
  #scids_df['scids'] = scids_df['scids'].astype(int) scids are already integer froms
  scids_df['collaboration_index'] = [corpus[(corpus['Authors_ID_list']
                                             .apply(lambda x: person in x)) & (corpus['authorcount'] > 1)]['authorcount'].mean() for person in scids_df['scids']]
  scids_df['collaboration_coefficient'] = (1 - (scids_df['fractional_equal']/scids_df['whole_fullcount']))#.fillna(0)
  #Is it better for these metrics to be just NaN rather than 0, for individuals who have zero publications? NaN seems reasonable as there is no collaboration when there is no publication.
  return scids_df


def find_unique_coauthors (corpus, scids_df):
  corpus['Authors_ID_list'] = corpus['Authors_ID_list'].apply(lambda x: [int(i) for i in x])
  #scids_df['scids'] = scids_df['scids'].astype(int)
  scids_df['all_coauthors_(list)'] = [[coauthor for sublist in corpus[corpus['Authors_ID_list'].apply(lambda x: person in x)]['Authors_ID_list'] for coauthor in sublist] for person in scids_df['scids']]
  scids_df['unique_coauthors_(set)'] = scids_df['all_coauthors_(list)'].apply(lambda x: set(x))
  scids_df['number_of_unique_COauthors_temp'] = scids_df['unique_coauthors_(set)'].apply(lambda x: len(x)-1)
  #To avoid negative values for authors with no coauthors (i.e all papers are sigle-authored)
  scids_df['number_of_unique_COauthors'] = scids_df['number_of_unique_COauthors_temp'].apply(lambda x: 0 if x < 0 else x)
  scids_df = scids_df.drop (columns = ['all_coauthors_(list)', 'unique_coauthors_(set)', 'number_of_unique_COauthors_temp'], axis = 1)
  return scids_df



if raw_corpus is not None:
  
  st.write ("File uploaded successfully!")
  corpus01, first_corpus = corpus_preprocess (raw_corpus)
  numberofdocs = len(corpus01)
  number_of_docs_removed = len(corpus01) - len(first_corpus)
  st.markdown (f"**UPDATE**: After removing duplicates and rows with missing information in essential columns, there are **<u>{numberofdocs}</u>** documents in the corpus. \n **<u>{number_of_docs_removed}</u>** document(s) were excluded (for missing data in essential columns: Author(s) ID, Document Type, or Year).", unsafe_allow_html=True)
  

  
  st.markdown("""<hr style="height:4px;border:none;color:#fe8100;background-color:#fe8100;" />""", unsafe_allow_html=True)
  
  #STEP 2 STARTS: Optional user input to select document type and/or publication years to analyze
  st.markdown ("### STEP 2")
  st.markdown ("**OPTIONAL: Select <u>document type</u> and/or <u>publication year(s)</u> to include in the analysis.  \n The document types most commonly included in analysis are **<u>Articles & Reviews**.</u>", unsafe_allow_html=True)
  document_types = corpus01['Document_Type'].unique()
  doctype = st.multiselect('', document_types, default=document_types)
  corpus01_doctype = corpus01.query('`Document_Type`.isin(@doctype)')


  Years = corpus01_doctype['Year'].unique()

  Years_selected = st.slider (label = "Drag the lower and upper end of the slider to set the range of publication years to include in the analysis.", min_value = min (Years), max_value = max (Years), value = (min (Years), max (Years)), step = 1)
  Years_selected = list(Years_selected)
  corpus01_doctype = corpus01_doctype [corpus01_doctype ['Year'].between(Years_selected[0], Years_selected[1])]
  doctype_Year_selection_lenght = len(corpus01_doctype)

  start_year = min(Years_selected)
  end_year = max(Years_selected)
  st.markdown (f"**UPDATE**: \nYou specified Document type: <u>**{doctype}**</u>, and \n Publication years: <u>**{start_year} to {end_year}**</u>.  \n The number of documents in the specified corpus is <u>**{doctype_Year_selection_lenght}**</u>.", unsafe_allow_html=True)

  #STEP 2 ENDS
  
  st.markdown("""<hr style="height:4px;border:none;color:#fe8100;background-color:#fe8100;" />""", unsafe_allow_html=True)
  # Final processing of the corpus with the 3 compound functions
  
  corpus = calculate_arithmetic_and_geometric_credit_schemes (corpus01_doctype)
  corpus = calculate_3_fractional_credit_schemes (corpus)
  corpus = calculate_3_harmonic_credit_schemes (corpus)

  
  
  
  #THIS WAS JUST FOR DEBUGGING, BUT EVERYTHING WORKS FINE; perhaps I'll just keep this feature in the code for now
  if st.button ("Preview pre-processed corpus"):
    st.write(corpus)

  st.markdown("""<hr style="height:4px;border:none;color:#fe8100;background-color:#fe8100;" />""", unsafe_allow_html=True)
  
  
  #STEP 3 STARTS
  st.markdown ("### STEP 3")
  st.markdown ("**Upload the csv file with the list of author Scopus IDs to be analysed. <u>IDs must be in the first column of the worksheet; only one ID per row.**</u>" ,unsafe_allow_html=True)
  scids_df = st.file_uploader (".", type = [".csv"])
  
  
  
  if scids_df is not None:

    st.write ("File uploaded successfully!")
    scids_df = pd.read_csv (scids_df)
    #We need to rename the first column to 'ID' from whatever the user labelled it
    first_column = scids_df.columns[0]
    scids_df = scids_df.rename(columns={first_column: 'ID'})
    #we also need to remove duplicates as I have found that this messes with results if an ID shows up more than once.
    scids_df = scids_df.drop_duplicates(subset =['ID'], keep='first')

    
    
    scids_df = extract_whole_and_straight_counts(corpus, scids_df)
    scids_df = extract_fractional_standard (corpus, scids_df)


    column_pairs = [
    ('fractional_credit_LAE', 'fractional_LAE'), 
    ('fractional_credit_FAE', 'fractional_FAE'),
    ('fractional_credit_FLAE', 'fractional_FLAE'),
    ('arithmetic_credit', 'arithmetic_standard'),
    ('arithmetic_credit_V', 'arithmetic_V'),
    ('golden_share_credit', 'golden_share'),
    ('geometric_credit', 'geometric_standard'),
    ('geometric_credit_adaptive', 'geometric_adaptive'),
    ('harmonic_credit_STD', 'harmonic_standard'),
    ('harmonic_credit_FLAE', 'harmonic_FLAE'),
    ('harmonic_credit_PAR', 'harmonic_parabolic')
    ]

    scids_df = Multiplex_extract_allocation_sum (corpus, scids_df, column_pairs)

    #Calculate first and last author proportion. This is the percentage of publications where the author is the first author or last author relative to the total number of publications
    scids_df['first_last_author_proportion'] = (scids_df['straight_firstauthor'] + scids_df['straight_lastauthor'])/scids_df['whole_fullcount']


    #COLLABORATION STUFF
    count_one_author_publications (corpus, scids_df)
    scids_df = calculate_collaborations_DC_CI_CC (corpus, scids_df)
    find_unique_coauthors (corpus, scids_df)
    scids_df = scids_df.drop (columns = ['number_of_unique_COauthors_temp', 'all_coauthors_(list)', 'unique_coauthors_(set)'], axis = 1)
    
    
    st.write (scids_df)


    st.markdown("""<hr style="height:4px;border:none;color:#fe8100;background-color:#fe8100;" />""", unsafe_allow_html=True)

    st.markdown ("*Thank you for using ***AuthormetriX***.    Kindly remember to cite the publication (full citation above).*",unsafe_allow_html=True)



  