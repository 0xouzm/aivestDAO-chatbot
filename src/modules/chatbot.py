import os
import streamlit as st
import tvscreener as tvs
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts.prompt import PromptTemplate
from langchain.callbacks import get_openai_callback
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.llms import OpenAI

# fix Error: module 'langchain' has no attribute 'verbose'
import langchain

langchain.verbose = False


class Chatbot:

    def __init__(self, model_name, temperature, vectors):
        self.model_name = model_name
        self.temperature = temperature
        self.vectors = vectors

    def conversational_chat(self, query):
        """
        Start a conversational chat with a model via Langchain
        """

        import requests
        import json

        address = sorted(query.split(' '), key=len, reverse=True)[0]
        url = "http://13.212.166.126:3000/v1/poc/getTxHistory?userAddress="+address
        payload = {}
        headers = {
            'User-Agent': 'Apifox/1.0.0',
            'Accept': '*/*',
            'Host': '13.212.166.126:3000',
            'Connection': 'keep-alive'
        }

        try:

            response = requests.request("GET", url, headers=headers, data=payload)

            data = json.loads(response.text)

            data_history = data['historyData']

        except:

            return ('There is something wrong with network, please come back to the conversation later')

        if (query.lower() == 'launch'):

            return ('You have successfully launched your tokenized model! Tell your friends to come to the "Fair Launch" 🛫buy your token, and leverage your crypto investment insights!')

        half = len(data_history) // 2

        data_1 = data_history[:half]

        data_2 = data_history[half:]

        data_1_token = []

        data_2_token = []

        data_1_fre = []

        data_2_fre = []

        for x in data_1:
            data_1_token.append(x.split("\t")[1])

            data_1_fre.append(float(x.split("\t")[3]))

        for x in data_2:
            data_2_token.append(x.split("\t")[1])

            data_2_fre.append(float(x.split("\t")[3]))

        token_1_div = (len(set(data_1_token)))

        token_2_div = (len(set(data_2_token)))

        token_div = token_1_div + token_2_div

        token_1_fre = (sum(data_1_fre))

        token_2_fre = (sum(data_2_fre))

        token_fre = token_1_fre + token_2_fre

        if (2*half) > 7:

            risk = 'risky'

        else:

            risk = 'conservative'

        if  (2*half) > 7:

            fre = 'frequent'

        else:

            fre = 'nonfrequent'

        if token_div > 10:

            div = 'diversified'

        else:

            div = 'nondiversified'

        if token_2_fre > token_1_fre:

            fre_trend = 'increasing'

        else:

            fre_trend = 'decreasing'

        if token_2_div > token_1_div:

            div_trend = 'increasing'

        else:

            div_trend = 'decreasing'

        if fre == 'frequent':
            fre_str = 'You are highly sensitive to market information and price fluctuations, demonstrating strong execution capabilities. You have confidence in the market, are self-assured about your trading strategy, possess courage, are willing to speculate, and can understand data trends. It is crucial for you to maintain mental stability, and you are likely to excel in your endeavors.'

        else:

            fre_str = 'You are very prudent, with strict risk management and a clear understanding of your investment approach. Therefore, factors such as a large volume of market information, changing market sentiment, and frequent price fluctuations do not prompt immediate investment decisions. Even if you sometimes envy others profits, you remain unaffected, carefully weighing the correlation between returns and high-risk situations.'

        if fre_trend == 'increasing':

            fre_trend_str = 'As time passes and your understanding of the cryptocurrency market grows, your enthusiasm for investing increases, accompanied by an expanding risk tolerance.'

        else:

            fre_trend_str = 'With time and increasing knowledge of the cryptocurrency market, you become more composed in your approach to investing, exercising greater caution in terms of risk.'

        if div == 'diversified':

            div_str = 'You favor risk diversification, enhancing the likelihood of returns by diversifying coin types to reduce correlation and allocating appropriate quantities.'

        else:

            div_str = 'Your focus is highly concentrated, spending most of your time monitoring the prices, fundamentals, and market information of a few cryptocurrencies. You base your investment decisions on past experiences and your understanding of their price movements.'

        if div_trend == 'increasing':

            div_trend_str = 'Over time, you become more open to investing in new projects and assets, welcoming new knowledge and market information.'

        else:

            div_trend_str = 'As time progresses, you gain clarity on which cryptocurrencies you excel at managing trades for, no longer spending time diversifying into assets you may not fully endorse.'

        investing_style_str = fre_str + ' ' + fre_trend_str + ' ' + div_str + ' ' + div_trend_str

        import pandas as pd
        from pypfopt import EfficientFrontier
        from pypfopt import risk_models
        from pypfopt import expected_returns
        from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
        df = pd.read_csv('src/modules/crypto_price.csv', parse_dates=True, index_col="Date")
        mu = expected_returns.mean_historical_return(df)
        S = risk_models.sample_cov(df)
        import random
        max_weight = 0.1 + 0.9*random.random()
        ef = EfficientFrontier(mu, S, weight_bounds=(0, max_weight))
        if risk == 'risky':
            raw_weights = ef.max_sharpe()
        else:
            raw_weights = ef.min_volatility()
        performance = list(ef.portfolio_performance())
        performance = [x / 12 for x in performance]
        performance_str = 'The best portfolio recommended by aivest with modern portfolio theory has monthly return of ' + str('{:.0%}'.format(performance[0])) + ' sharpe ratio of ' + str('{:.0%}'.format(performance[2]))
        weights = (pd.Series(raw_weights))
        latest_prices = get_latest_prices(df)
        df_market_cap = pd.read_csv('src/modules/crypto_market_cap.csv', parse_dates=True, index_col="Date")
        latest_market_cap = get_latest_prices(df_market_cap)
        price_min = df.min(axis=0)
        price_max = df.max(axis=0)
        max_drawdown = 1 - price_min / price_max
        df = pd.concat([weights, latest_prices, latest_market_cap, mu / 12, max_drawdown], axis=1)
        df.columns = ['Weight', 'Latest_Price', 'Latest_Market_Cap', 'Monthly_Return', 'Max_Drawdown']
        pd.set_option("display.precision", 3)
        df = df.loc[(df['Weight'] >= 0.01)]
        portfolio_max_drawdown = (df['Weight']*df['Max_Drawdown']).sum()
        info_str = (df.to_json())
        final_str = 'Thanks for your info! Here is the investing style analyzed by aivest with wallet address above: '+ investing_style_str + '\n\n' + performance_str + ' and max drawdown of '+str('{:.0%}'.format(portfolio_max_drawdown))+ 'Here you can see more details:'+ '\n\n' + info_str


        len_history = len(st.session_state["history"])

        qa_template = """
        You are a financial expert with crypto market experience.
        If question contains wallet address, output investing style with bullet points with seperate lines in the begining.
        Use all info in the final_str to answer the question and include monthly return, sharpe ratio and max drawdown in the answer .
        Output the records from the JSON data and format it as a markdown formatted table instead of a code-box with Weight, Monthly Return and Max Drawdown in 2 digits percentage, Latest Price and Latest Market Cap in float. Include the sentence "Next action: Kindly tell me 'Launch', once you are ready to tokenize and fair launch your portfolio model.🚀" with a new line if and only if question contains wallet address. 
        Using the chatgpt to answer the question if no relevant context is found.
        Include the sentence "Disclaimer: The crypto market is risky, investing should be approached cautiously." wih a new line if and only if the question is related to investment.
        context: {context}
        final_str: {final_str}
        =========
        question: {question}
        ======
        """

        QA_PROMPT = PromptTemplate(template=qa_template,
                                   input_variables=["context", "question", "final_str"])

        llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature)

        retriever = self.vectors.as_retriever()

        chain = ConversationalRetrievalChain.from_llm(llm=llm,
                                                      retriever=retriever, verbose=True, return_source_documents=True,
                                                      max_tokens_limit=4097,
                                                      combine_docs_chain_kwargs={'prompt': QA_PROMPT})

        chain_input = {"question": query, "chat_history": st.session_state["history"], "final_str": final_str}

        result = chain(chain_input)

        st.session_state["history"].append((query, result["answer"]))

        if len_history < 5:

            return result['answer']

        else:

            return (
                "Thank you for your participation！ We will limit the test to 5 times. We hope you will learn more about aivestDAO’s service.")
