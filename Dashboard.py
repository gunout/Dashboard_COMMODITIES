# dashboard_commodities.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import random
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Commodities - Marchés des Matières Premières",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(45deg, #FFD700, #FF6B00, #DC143C, #228B22);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        padding: 1rem;
    }
    .commodity-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .commodity-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .commodity-change {
        font-size: 1.2rem;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        display: inline-block;
        margin-top: 0.5rem;
    }
    .positive { background-color: rgba(40, 167, 69, 0.2); color: #28a745; border: 2px solid #28a745; }
    .negative { background-color: rgba(220, 53, 69, 0.2); color: #dc3545; border: 2px solid #dc3545; }
    .neutral { background-color: rgba(108, 117, 125, 0.2); color: #6c757d; border: 2px solid #6c757d; }
    .section-header {
        color: #0055A4;
        border-bottom: 3px solid #FF6B00;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        font-size: 1.8rem;
    }
    .commodity-icon {
        font-size: 2rem;
        margin-right: 1rem;
    }
    .metric-highlight {
        background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem;
    }
    .volatility-indicator {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-weight: bold;
    }
    .low-vol { background-color: #d4edda; color: #155724; }
    .medium-vol { background-color: #fff3cd; color: #856404; }
    .high-vol { background-color: #f8d7da; color: #721c24; }
    .category-energy { background: linear-gradient(135deg, #FFD700, #FF8C00); }
    .category-metals { background: linear-gradient(135deg, #C0C0C0, #B8860B); }
    .category-agri { background: linear-gradient(135deg, #32CD32, #006400); }
    .category-softs { background: linear-gradient(135deg, #FFB6C1, #8B4513); }
</style>
""", unsafe_allow_html=True)

class CommodityDashboard:
    def __init__(self):
        self.commodities = self.define_commodities()
        self.historical_data = self.initialize_historical_data()
        self.current_data = self.initialize_current_data()
        self.market_data = self.initialize_market_data()
        
    def define_commodities(self):
        """Définit les commodités avec leurs caractéristiques"""
        return {
            'BRENT': {
                'nom': 'Pétrole Brent',
                'symbole': 'BRENT',
                'icone': '🛢️',
                'categorie': 'Énergie',
                'unite': 'USD/baril',
                'prix_base': 85.0,
                'volatilite': 2.5,
                'production_mondiale': 82.0,  # millions barils/jour
                'reserves': 1500.0,  # milliards barils
                'pays_producteurs': ['Arabie Saoudite', 'Russie', 'USA', 'Irak'],
                'description': 'Référence mondiale du pétrole brut'
            },
            'WTI': {
                'nom': 'Pétrole WTI',
                'symbole': 'WTI',
                'icone': '⛽',
                'categorie': 'Énergie',
                'unite': 'USD/baril',
                'prix_base': 82.5,
                'volatilite': 2.8,
                'production_mondiale': 78.0,
                'reserves': 500.0,
                'pays_producteurs': ['USA', 'Canada', 'Mexique'],
                'description': 'Pétrole américain de référence'
            },
            'GOLD': {
                'nom': 'Or',
                'symbole': 'GOLD',
                'icone': '🥇',
                'categorie': 'Métaux Précieux',
                'unite': 'USD/once',
                'prix_base': 1950.0,
                'volatilite': 1.2,
                'production_mondiale': 3500.0,  # tonnes/an
                'reserves': 54000.0,
                'pays_producteurs': ['Chine', 'Australie', 'Russie', 'USA'],
                'description': 'Valeur refuge traditionnelle'
            },
            'SILVER': {
                'nom': 'Argent',
                'symbole': 'SILVER',
                'icone': '🥈',
                'categorie': 'Métaux Précieux',
                'unite': 'USD/once',
                'prix_base': 23.5,
                'volatilite': 2.1,
                'production_mondiale': 25000.0,
                'reserves': 530000.0,
                'pays_producteurs': ['Mexique', 'Pérou', 'Chine'],
                'description': 'Métal précieux industriel'
            },
            'COPPER': {
                'nom': 'Cuivre',
                'symbole': 'COPPER',
                'icone': '🔴',
                'categorie': 'Métaux Industriels',
                'unite': 'USD/livre',
                'prix_base': 3.85,
                'volatilite': 1.8,
                'production_mondiale': 22.0,  # millions tonnes/an
                'reserves': 870.0,
                'pays_producteurs': ['Chili', 'Pérou', 'Chine'],
                'description': 'Baromètre économique mondial'
            },
            'WHEAT': {
                'nom': 'Blé',
                'symbole': 'WHEAT',
                'icone': '🌾',
                'categorie': 'Agriculture',
                'unite': 'USD/boisseau',
                'prix_base': 6.25,
                'volatilite': 3.2,
                'production_mondiale': 780.0,  # millions tonnes/an
                'reserves': 280.0,
                'pays_producteurs': ['Chine', 'Inde', 'Russie', 'USA'],
                'description': 'Céréale alimentaire majeure'
            },
            'CORN': {
                'nom': 'Maïs',
                'symbole': 'CORN',
                'icone': '🌽',
                'categorie': 'Agriculture',
                'unite': 'USD/boisseau',
                'prix_base': 4.80,
                'volatilite': 2.9,
                'production_mondiale': 1200.0,
                'reserves': 320.0,
                'pays_producteurs': ['USA', 'Chine', 'Brésil'],
                'description': 'Céréale pour alimentation animale et humaine'
            },
            'SOYBEANS': {
                'nom': 'Soja',
                'symbole': 'SOYBEANS',
                'icone': '🫘',
                'categorie': 'Agriculture',
                'unite': 'USD/boisseau',
                'prix_base': 12.80,
                'volatilite': 2.7,
                'production_mondiale': 350.0,
                'reserves': 90.0,
                'pays_producteurs': ['USA', 'Brésil', 'Argentine'],
                'description': 'Protéine végétale principale'
            },
            'COFFEE': {
                'nom': 'Café',
                'symbole': 'COFFEE',
                'icone': '☕',
                'categorie': 'Softs',
                'unite': 'USD/livre',
                'prix_base': 1.85,
                'volatilite': 4.1,
                'production_mondiale': 10.5,  # millions tonnes/an
                'reserves': 25.0,
                'pays_producteurs': ['Brésil', 'Vietnam', 'Colombie'],
                'description': 'Boisson la plus échangée après le pétrole'
            }
        }
    
    def initialize_historical_data(self):
        """Initialise les données historiques des commodités"""
        dates = pd.date_range('2020-01-01', datetime.now(), freq='D')
        data = []
        
        for date in dates:
            for symbole, info in self.commodities.items():
                # Prix de base
                base_price = info['prix_base']
                
                # Impact des événements mondiaux
                global_impact = 1.0
                
                # Crise COVID (2020)
                if date.year == 2020 and date.month <= 6:
                    if info['categorie'] == 'Énergie':
                        global_impact *= random.uniform(0.5, 0.8)  # Effondrement pétrole
                    else:
                        global_impact *= random.uniform(0.9, 1.1)
                # Reprise post-COVID (2021)
                elif date.year == 2021:
                    global_impact *= random.uniform(1.05, 1.25)
                # Guerre Ukraine (2022)
                elif date.year == 2022 and date.month >= 2:
                    if info['symbole'] in ['WHEAT', 'CORN']:
                        global_impact *= random.uniform(1.2, 1.6)  # Hausse céréales
                    elif info['categorie'] == 'Énergie':
                        global_impact *= random.uniform(1.1, 1.4)
                # Tensions récentes
                elif date.year >= 2023:
                    global_impact *= random.uniform(0.95, 1.15)
                
                # Volatilité quotidienne basée sur le profil de volatilité
                daily_volatility = random.normalvariate(1, info['volatilite']/100)
                
                # Tendance saisonnière
                seasonal = 1 + 0.005 * np.sin(2 * np.pi * date.dayofyear / 365)
                
                prix_actuel = base_price * global_impact * daily_volatility * seasonal
                
                data.append({
                    'date': date,
                    'symbole': symbole,
                    'nom': info['nom'],
                    'categorie': info['categorie'],
                    'prix': prix_actuel,
                    'volume': random.uniform(100000, 5000000),
                    'volatilite_jour': abs(daily_volatility - 1) * 100
                })
        
        return pd.DataFrame(data)
    
    def initialize_current_data(self):
        """Initialise les données courantes"""
        current_data = []
        for symbole, info in self.commodities.items():
            # Dernières données historiques
            last_data = self.historical_data[self.historical_data['symbole'] == symbole].iloc[-1]
            
            # Variations simulées
            change_pct = random.uniform(-3.0, 3.0)
            
            current_data.append({
                'symbole': symbole,
                'nom': info['nom'],
                'icone': info['icone'],
                'categorie': info['categorie'],
                'unite': info['unite'],
                'prix': last_data['prix'] * (1 + change_pct/100),
                'change_pct': change_pct,
                'volatilite': info['volatilite'],
                'production_mondiale': info['production_mondiale'],
                'reserves': info['reserves'],
                'pays_producteurs': info['pays_producteurs'],
                'volume_jour': random.uniform(500000, 5000000),
                'spread': random.uniform(0.1, 0.5)
            })
        
        return pd.DataFrame(current_data)
    
    def initialize_market_data(self):
        """Initialise les données des marchés mondiaux"""
        indices = {
            'S&P 500': {'valeur': 4500, 'change': 0.0, 'secteur': 'USA'},
            'NASDAQ': {'valeur': 14000, 'change': 0.0, 'secteur': 'USA Tech'},
            'DAX': {'valeur': 16000, 'change': 0.0, 'secteur': 'Allemagne'},
            'CAC 40': {'valeur': 7200, 'change': 0.0, 'secteur': 'France'},
            'FTSE 100': {'valeur': 7500, 'change': 0.0, 'secteur': 'UK'},
            'Nikkei 225': {'valeur': 33000, 'change': 0.0, 'secteur': 'Japon'}
        }
        
        devises = {
            'EUR/USD': {'valeur': 1.0850, 'change': 0.0},
            'USD/JPY': {'valeur': 148.50, 'change': 0.0},
            'GBP/USD': {'valeur': 1.2650, 'change': 0.0},
            'USD/CHF': {'valeur': 0.8850, 'change': 0.0}
        }
        
        return {'indices': indices, 'devises': devises}
    
    def update_live_data(self):
        """Met à jour les données en temps réel"""
        for idx in self.current_data.index:
            symbole = self.current_data.loc[idx, 'symbole']
            
            # Mise à jour des prix
            if random.random() < 0.6:  # 60% de chance de changement
                variation = random.uniform(-1.5, 1.5)
                
                self.current_data.loc[idx, 'prix'] *= (1 + variation/100)
                self.current_data.loc[idx, 'change_pct'] = variation
                
                # Mise à jour du volume
                self.current_data.loc[idx, 'volume_jour'] *= random.uniform(0.7, 1.4)
    
    def display_header(self):
        """Affiche l'en-tête du dashboard"""
        st.markdown(
            '<h1 class="main-header">🛢️ DASHBOARD COMMODITIES - MARCHÉS DES MATIÈRES PREMIÈRES</h1>', 
            unsafe_allow_html=True
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(
                '<div style="text-align: center; background: linear-gradient(45deg, #FFD700, #FF6B00); '
                'color: white; padding: 1rem; border-radius: 10px; margin-bottom: 2rem;">'
                '<h3>🔴 SURVEILLANCE EN TEMPS RÉEL DES MARCHÉS DE MATIÈRES PREMIÈRES</h3>'
                '</div>', 
                unsafe_allow_html=True
            )
        
        current_time = datetime.now().strftime('%H:%M:%S')
        st.sidebar.markdown(f"**🕐 Dernière mise à jour: {current_time}**")
    
    def display_commodity_cards(self):
        """Affiche les cartes de commodités principales"""
        st.markdown('<h3 class="section-header">💰 PRIX DES COMMODITÉS EN TEMPS RÉEL</h3>', 
                   unsafe_allow_html=True)
        
        # Grouper par catégorie
        categories = self.current_data['categorie'].unique()
        
        for categorie in categories:
            st.markdown(f'<h4 style="color: #0055A4; margin-top: 1rem;">{categorie}</h4>', 
                       unsafe_allow_html=True)
            
            cat_data = self.current_data[self.current_data['categorie'] == categorie]
            cols = st.columns(len(cat_data))
            
            for idx, (_, commodity) in enumerate(cat_data.iterrows()):
                with cols[idx]:
                    change_class = "positive" if commodity['change_pct'] > 0 else "negative" if commodity['change_pct'] < 0 else "neutral"
                    card_class = f"commodity-card category-{categorie.lower().replace(' ', '').replace('é', 'e')}"
                    
                    st.markdown(f"""
                    <div class="{card_class}">
                        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                            <span class="commodity-icon">{commodity['icone']}</span>
                            <div>
                                <h3 style="margin: 0; font-size: 1.2rem;">{commodity['symbole']}</h3>
                                <p style="margin: 0; opacity: 0.9; font-size: 0.9rem;">{commodity['nom']}</p>
                            </div>
                        </div>
                        <div class="commodity-value">{commodity['prix']:.2f}</div>
                        <div style="font-size: 0.9rem; opacity: 0.8;">{commodity['unite']}</div>
                        <div class="commodity-change {change_class}">
                            {commodity['change_pct']:+.2f}%
                        </div>
                        <div style="margin-top: 1rem; font-size: 0.8rem;">
                            📊 Vol: {commodity['volume_jour']:,.0f}<br>
                            📈 Volatilité: {commodity['volatilite']:.1f}%
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    def display_key_metrics(self):
        """Affiche les métriques clés"""
        st.markdown('<h3 class="section-header">📊 INDICATEURS MARCHÉ</h3>', 
                   unsafe_allow_html=True)
        
        # Calcul des métriques globales
        avg_change = self.current_data['change_pct'].mean()
        total_volume = self.current_data['volume_jour'].sum()
        strongest_commodity = self.current_data.loc[self.current_data['change_pct'].idxmax()]
        weakest_commodity = self.current_data.loc[self.current_data['change_pct'].idxmin()]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Performance Moyenne",
                f"{avg_change:+.2f}%",
                "Journalier",
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                "Volume Total Journalier",
                f"${total_volume:,.0f}",
                f"{random.randint(-8, 12)}% vs hier"
            )
        
        with col3:
            st.metric(
                "Plus Forte Hausse",
                f"{strongest_commodity['symbole']}",
                f"{strongest_commodity['change_pct']:+.2f}%"
            )
        
        with col4:
            st.metric(
                "Plus Forte Baisse",
                f"{weakest_commodity['symbole']}",
                f"{weakest_commodity['change_pct']:+.2f}%"
            )
    
    def create_price_overview(self):
        """Crée la vue d'ensemble des prix"""
        st.markdown('<h3 class="section-header">📈 ANALYSE DES PRIX HISTORIQUES</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "Évolution Historique", 
            "Analyse par Catégorie", 
            "Volatilité", 
            "Performances Relatives"
        ])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Sélection des commodités à afficher
                selected_commodities = st.multiselect(
                    "Sélectionnez les commodités:",
                    list(self.commodities.keys()),
                    default=['BRENT', 'GOLD', 'COPPER', 'WHEAT']
                )
            
            with col2:
                # Période d'analyse
                period = st.selectbox(
                    "Période d'analyse:",
                    ['1 an', '2 ans', '3 ans', 'Toute la période'],
                    index=0
                )
            
            # Filtrage des données
            filtered_data = self.historical_data[
                self.historical_data['symbole'].isin(selected_commodities)
            ]
            
            if period != 'Toute la période':
                years = int(period.split()[0])
                cutoff_date = datetime.now() - timedelta(days=365 * years)
                filtered_data = filtered_data[filtered_data['date'] >= cutoff_date]
            
            fig = px.line(filtered_data, 
                         x='date', 
                         y='prix',
                         color='symbole',
                         title=f'Évolution des Prix des Commodités ({period})',
                         color_discrete_sequence=px.colors.qualitative.Bold)
            fig.update_layout(yaxis_title="Prix (USD)")
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Analyse par catégorie
            fig = px.box(self.historical_data, 
                        x='categorie', 
                        y='prix',
                        title='Distribution des Prix par Catégorie',
                        color='categorie')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                # Volatilité historique
                volatilite_data = self.historical_data.groupby('symbole')['volatilite_jour'].mean().reset_index()
                fig = px.bar(volatilite_data, 
                            x='symbole', 
                            y='volatilite_jour',
                            title='Volatilité Historique Moyenne (%)',
                            color='symbole',
                            color_discrete_sequence=px.colors.qualitative.Bold)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Volatilité récente (30 derniers jours)
                recent_data = self.historical_data[
                    self.historical_data['date'] > (datetime.now() - timedelta(days=30))
                ]
                recent_vol = recent_data.groupby('symbole')['volatilite_jour'].std().reset_index()
                
                fig = px.scatter(recent_vol, 
                               x='symbole', 
                               y='volatilite_jour',
                               size='volatilite_jour',
                               title='Volatilité Récente (30 jours)',
                               color='symbole',
                               size_max=40)
                st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            # Performance relative
            performance_data = []
            for symbole in self.commodities.keys():
                commodity_data = self.historical_data[self.historical_data['symbole'] == symbole]
                if len(commodity_data) > 0:
                    start_price = commodity_data.iloc[0]['prix']
                    end_price = commodity_data.iloc[-1]['prix']
                    performance = ((end_price - start_price) / start_price) * 100
                    performance_data.append({
                        'symbole': symbole,
                        'performance': performance,
                        'categorie': self.commodities[symbole]['categorie']
                    })
            
            performance_df = pd.DataFrame(performance_data)
            fig = px.bar(performance_df, 
                        x='symbole', 
                        y='performance',
                        color='categorie',
                        title='Performance Totale depuis 2020 (%)',
                        color_discrete_sequence=px.colors.qualitative.Bold)
            st.plotly_chart(fig, use_container_width=True)
    
    def create_supply_demand_analysis(self):
        """Analyse offre/demande"""
        st.markdown('<h3 class="section-header">⚖️ ANALYSE OFFRE/DEMANDE</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Production Mondiale", "Réserves", "Facteurs d'Influence"])
        
        with tab1:
            # Production mondiale par commodité
            production_data = []
            for symbole, info in self.commodities.items():
                production_data.append({
                    'symbole': symbole,
                    'nom': info['nom'],
                    'production': info['production_mondiale'],
                    'categorie': info['categorie']
                })
            
            production_df = pd.DataFrame(production_data)
            fig = px.bar(production_df, 
                        x='symbole', 
                        y='production',
                        color='categorie',
                        title='Production Mondiale par Commodité',
                        labels={'production': 'Production (unités spécifiques)'})
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Réserves mondiales
            reserves_data = []
            for symbole, info in self.commodities.items():
                reserves_data.append({
                    'symbole': symbole,
                    'nom': info['nom'],
                    'reserves': info['reserves'],
                    'categorie': info['categorie']
                })
            
            reserves_df = pd.DataFrame(reserves_data)
            fig = px.pie(reserves_df, 
                        values='reserves', 
                        names='symbole',
                        title='Répartition des Réserves Mondiales par Commodité',
                        color='categorie')
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("Facteurs Influençant les Prix")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 📈 Facteurs Haussiers
                
                **🛢️ Tensions Géopolitiques:**
                - Conflits au Moyen-Orient
                - Sanctions internationales
                - Instabilité politique
                
                **📊 Croissance Économique:**
                - Demande industrielle
                - Construction d'infrastructures
                - Consommation énergétique
                
                **🌍 Facteurs Environnementaux:**
                - Conditions météo défavorables
                - Catastrophes naturelles
                - Changement climatique
                """)
            
            with col2:
                st.markdown("""
                ### 📉 Facteurs Baissiers
                
                **💸 Récession Économique:**
                - Baisse de la demande
                - Contraction industrielle
                - Chômage élevé
                
                **🔄 Innovation Technologique:**
                - Énergies alternatives
                - Efficacité énergétique
                - Substitutions de matériaux
                
                **🏦 Politiques Monétaires:**
                - Dollar fort
                - Taux d'intérêt élevés
                - Politiques restrictives
                """)
    
    def create_technical_analysis(self):
        """Analyse technique avancée"""
        st.markdown('<h3 class="section-header">🔬 ANALYSE TECHNIQUE AVANCÉE</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Indicateurs Techniques", "Patterns de Trading", "Signaux"])
        
        with tab1:
            commodite_selectionnee = st.selectbox("Sélectionnez une commodité:", 
                                                list(self.commodities.keys()))
            
            if commodite_selectionnee:
                commodite_data = self.historical_data[
                    self.historical_data['symbole'] == commodite_selectionnee
                ].copy()
                
                # Calcul des indicateurs techniques
                commodite_data['MA20'] = commodite_data['prix'].rolling(window=20).mean()
                commodite_data['MA50'] = commodite_data['prix'].rolling(window=50).mean()
                commodite_data['RSI'] = self.calculate_rsi(commodite_data['prix'])
                commodite_data['Bollinger_High'], commodite_data['Bollinger_Low'] = self.calculate_bollinger_bands(commodite_data['prix'])
                
                fig = make_subplots(rows=3, cols=1, 
                                  shared_xaxes=True, 
                                  vertical_spacing=0.05,
                                  subplot_titles=('Prix et Moyennes Mobiles', 'Bandes de Bollinger', 'RSI'),
                                  row_heights=[0.5, 0.25, 0.25])
                
                # Prix et moyennes mobiles
                fig.add_trace(go.Scatter(x=commodite_data['date'], y=commodite_data['prix'],
                                       name='Prix', line=dict(color='#0055A4')), row=1, col=1)
                fig.add_trace(go.Scatter(x=commodite_data['date'], y=commodite_data['MA20'],
                                       name='MM20', line=dict(color='orange')), row=1, col=1)
                fig.add_trace(go.Scatter(x=commodite_data['date'], y=commodite_data['MA50'],
                                       name='MM50', line=dict(color='red')), row=1, col=1)
                
                # Bandes de Bollinger
                fig.add_trace(go.Scatter(x=commodite_data['date'], y=commodite_data['Bollinger_High'],
                                       name='Bollinger High', line=dict(color='gray', dash='dash')), row=2, col=1)
                fig.add_trace(go.Scatter(x=commodite_data['date'], y=commodite_data['prix'],
                                       name='Prix', line=dict(color='#0055A4'), showlegend=False), row=2, col=1)
                fig.add_trace(go.Scatter(x=commodite_data['date'], y=commodite_data['Bollinger_Low'],
                                       name='Bollinger Low', line=dict(color='gray', dash='dash'), 
                                       fill='tonexty'), row=2, col=1)
                
                # RSI
                fig.add_trace(go.Scatter(x=commodite_data['date'], y=commodite_data['RSI'],
                                       name='RSI', line=dict(color='purple')), row=3, col=1)
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
                
                fig.update_layout(height=800, title_text=f"Analyse Technique - {commodite_selectionnee}")
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("Patterns de Trading Identifiés")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 📈 Patterns Haussiers
                
                **🔺 Double Bottom (OR):**
                - Support solide à 1900 USD
                - Rebond technique confirmé
                - Objectif: 2050 USD
                
                **🔼 Triangle Ascendant (PÉTROLE):**
                - Consolidation haussière
                - Rupture imminente
                - Volume croissant
                
                **🚀 Breakout (CUIVRE):**
                - Résistance franchie à 3.80 USD
                - Momentum positif
                - Retest réussi
                """)
            
            with col2:
                st.markdown("""
                ### 📉 Patterns Baissiers
                
                **🔻 Double Top (BLÉ):**
                - Résistance à 6.50 USD
                - Échec de rupture
                - Objectif: 5.80 USD
                
                **🔽 Tête et Épaules (ARGENT):**
                - Pattern de retournement
                - Volume de distribution
                - Ligne cou brisée
                
                **📉 Channel Descendant (CAFÉ):**
                - Série de plus bas
                - Résistance descendante
                - Momentum négatif
                """)
        
        with tab3:
            st.subheader("Signaux de Trading")
            
            # Génération de signaux simulés
            signaux = []
            for symbole in self.commodities.keys():
                signal_type = random.choice(['ACHAT', 'VENTE', 'NEUTRE'])
                force = random.randint(60, 95)
                horizon = random.choice(['Court terme', 'Moyen terme', 'Long terme'])
                
                signaux.append({
                    'Commodité': symbole,
                    'Signal': signal_type,
                    'Force': f"{force}%",
                    'Horizon': horizon,
                    'Prix Cible': self.current_data[self.current_data['symbole'] == symbole]['prix'].iloc[0] * 
                                 random.uniform(0.90, 1.10)
                })
            
            signaux_df = pd.DataFrame(signaux)
            st.dataframe(signaux_df, use_container_width=True)
    
    def calculate_rsi(self, prices, window=14):
        """Calcule le RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_bollinger_bands(self, prices, window=20, num_std=2):
        """Calcule les bandes de Bollinger"""
        rolling_mean = prices.rolling(window=window).mean()
        rolling_std = prices.rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        return upper_band, lower_band
    
    def create_market_analysis(self):
        """Analyse des marchés mondiaux"""
        st.markdown('<h3 class="section-header">🌍 ANALYSE DES MARCHÉS MONDAUX</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Indices Mondiaux", "Devises", "Analyse Macro"])
        
        with tab1:
            st.subheader("Performances des Indices Mondiaux")
            
            cols = st.columns(3)
            indices_list = list(self.market_data['indices'].items())
            
            for i, (indice, data) in enumerate(indices_list):
                with cols[i % 3]:
                    data['change'] = random.uniform(-2, 2)  # Mise à jour simulée
                    st.metric(
                        indice,
                        f"{data['valeur']:,.0f}",
                        f"{data['change']:+.2f}%",
                        delta_color="normal"
                    )
        
        with tab2:
            st.subheader("Taux de Change")
            
            cols = st.columns(2)
            devises_list = list(self.market_data['devises'].items())
            
            for i, (devise, data) in enumerate(devises_list):
                with cols[i % 2]:
                    data['change'] = random.uniform(-0.8, 0.8)
                    st.metric(
                        devise,
                        f"{data['valeur']:.4f}",
                        f"{data['change']:+.2f}%",
                        delta_color="normal"
                    )
        
        with tab3:
            st.subheader("Indicateurs Macroéconomiques")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 🇺🇸 Économie Américaine
                
                **📊 Inflation:** 3.2% (cible: 2.0%)
                **💵 Taux Directeurs:** 5.25%-5.50%
                **📈 Croissance PIB:** 2.1%
                **👥 Chômage:** 3.8%
                **🏠 Marché Immobilier:** Stable
                
                ### 🇪🇺 Zone Euro
                
                **📊 Inflation:** 2.4% (cible: 2.0%)
                **💵 Taux Directeurs:** 4.5%
                **📈 Croissance PIB:** 0.5%
                **👥 Chômage:** 6.5%
                **🏭 Production Industrielle:** +0.3%
                """)
            
            with col2:
                st.markdown("""
                ### 🌍 Économie Mondiale
                
                **📊 Croissance Mondiale:** 3.1%
                **🛢️ Demande Pétrolière:** 102M barils/jour
                **🏭 Production Industrielle:** +2.8%
                **📦 Commerce Mondial:** +1.7%
                
                ### 🏦 Politiques Monétaires
                
                **🇺🇸 Fed:** Hawkish pause
                **🇪🇺 BCE:** Dovish pivot
                **🇬🇧 BoE:** Attentiste
                **🇯🇵 BoJ:** Ultra-dovish
                **🇨🇳 PBOC:** Stimulus modéré
                """)
    
    def create_risk_analysis(self):
        """Analyse des risques"""
        st.markdown('<h3 class="section-header">⚠️ ANALYSE DES RISQUES</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Risques par Commodité", "Stress Tests", "Stratégies de Couverture"])
        
        with tab1:
            st.subheader("Évaluation des Risques par Commodité")
            
            risk_data = []
            for symbole, info in self.commodities.items():
                risk_score = random.randint(25, 85)
                risk_level = "FAIBLE" if risk_score < 40 else "MOYEN" if risk_score < 70 else "ÉLEVÉ"
                
                risk_data.append({
                    'Commodité': info['nom'],
                    'Symbole': symbole,
                    'Score Risque': risk_score,
                    'Niveau': risk_level,
                    'Risque Géopolitique': random.randint(20, 90),
                    'Risque Climatique': random.randint(15, 80),
                    'Risque de Demande': random.randint(25, 75)
                })
            
            risk_df = pd.DataFrame(risk_data)
            st.dataframe(risk_df, use_container_width=True)
        
        with tab2:
            st.subheader("Scénarios de Stress Test")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 📉 Scénario Dégradé
                
                **Hypothèses:**
                - Récession mondiale profonde
                - Pétrole à $50/baril
                - USD +20%
                - Chute de la demande industrielle
                
                **Impacts:**
                - Pétrole: -40%
                - Métaux industriels: -35%
                - Agriculture: -25%
                - Or: +15% (valeur refuge)
                
                **Probabilité:** 20%
                """)
            
            with col2:
                st.markdown("""
                ### 📈 Scénario Optimiste
                
                **Hypothèses:**
                - Croissance robuste mondiale
                - Pétrole à $120/baril
                - USD -15%
                - Boom des infrastructures
                
                **Impacts:**
                - Pétrole: +40%
                - Métaux industriels: +50%
                - Agriculture: +30%
                - Or: -10%
                
                **Probabilité:** 25%
                """)
        
        with tab3:
            st.subheader("Stratégies de Couverture")
            
            st.markdown("""
            ### 🛡️ Instruments de Couverture
            
            **📊 Futures/Forwards:**
            - Contrats standardisés sur marchés organisés
            - Liquidité élevée
            - Maturités variées (mensuelles, trimestrielles)
            
            **🔄 Options:**
            - Protection asymétrique
            - Prime à payer
            - Flexibilité stratégique
            - Calls/Puts selon le scénario
            
            **⚖️ ETF Sectoriels:**
            - Exposition sectorielle
            - Liquidité quotidienne
            - Frais modérés
            - Inverse/Levraged disponibles
            
            **💱 Spread Trading:**
            - Paires de commodités corrélées
            - Spreads calendaires
            - Arbitrage géographique
            """)
    
    def create_sidebar(self):
        """Crée la sidebar avec les contrôles"""
        st.sidebar.markdown("## 🎛️ CONTRÔLES D'ANALYSE")
        
        # Catégories à afficher
        st.sidebar.markdown("### 🏷️ Catégories à surveiller")
        categories = list(self.current_data['categorie'].unique())
        categories_selectionnees = st.sidebar.multiselect(
            "Sélectionnez les catégories:",
            categories,
            default=categories
        )
        
        # Période d'analyse
        st.sidebar.markdown("### 📅 Période d'analyse")
        date_debut = st.sidebar.date_input("Date de début", 
                                         value=datetime.now() - timedelta(days=365))
        date_fin = st.sidebar.date_input("Date de fin", 
                                       value=datetime.now())
        
        # Options d'analyse
        st.sidebar.markdown("### ⚙️ Options d'analyse")
        auto_refresh = st.sidebar.checkbox("Rafraîchissement automatique", value=True)
        show_advanced = st.sidebar.checkbox("Indicateurs avancés", value=True)
        alert_threshold = st.sidebar.slider("Seuil d'alerte (%)", 1.0, 10.0, 3.0)
        
        # Bouton de rafraîchissement
        if st.sidebar.button("🔄 Rafraîchir les données"):
            self.update_live_data()
            st.rerun()
        
        # Alertes en temps réel
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 🔔 ALERTES EN TEMPS RÉEL")
        
        for _, commodity in self.current_data.iterrows():
            if abs(commodity['change_pct']) > alert_threshold:
                alert_type = "warning" if commodity['change_pct'] > 0 else "error"
                if alert_type == "warning":
                    st.sidebar.warning(
                        f"{commodity['icone']} {commodity['symbole']}: "
                        f"{commodity['change_pct']:+.2f}%"
                    )
                else:
                    st.sidebar.error(
                        f"{commodity['icone']} {commodity['symbole']}: "
                        f"{commodity['change_pct']:+.2f}%"
                    )
        
        return {
            'categories_selectionnees': categories_selectionnees,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'auto_refresh': auto_refresh,
            'show_advanced': show_advanced,
            'alert_threshold': alert_threshold
        }

    def run_dashboard(self):
        """Exécute le dashboard complet"""
        # Mise à jour des données
        self.update_live_data()
        
        # Sidebar
        controls = self.create_sidebar()
        
        # Header
        self.display_header()
        
        # Cartes de commodités
        self.display_commodity_cards()
        
        # Métriques clés
        self.display_key_metrics()
        
        # Navigation par onglets
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📈 Vue d'Ensemble", 
            "⚖️ Offre/Demande", 
            "🔬 Technique", 
            "🌍 Marchés", 
            "⚠️ Risques", 
            "💡 Insights"
        ])
        
        with tab1:
            self.create_price_overview()
        
        with tab2:
            self.create_supply_demand_analysis()
        
        with tab3:
            self.create_technical_analysis()
        
        with tab4:
            self.create_market_analysis()
        
        with tab5:
            self.create_risk_analysis()
        
        with tab6:
            st.markdown("## 💡 INSIGHTS STRATÉGIQUES")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ### 🎯 TENDANCES DES COMMODITÉS
                
                **🛢️ Énergies:**
                - Tensions géopolitiques soutiennent les prix
                - Transition énergétique à moyen terme
                - Demande asiatique robuste
                - Perspective: Stable à haussière
                
                **🥇 Métaux Précieux:**
                - Or: valeur refuge en période d'incertitude
                - Argent: double usage industriel et spéculatif
                - Perspective: Neutre à haussière
                
                **🔴 Métaux Industriels:**
                - Cuivre: baromètre économique mondial
                - Demande chinoise cruciale
                - Perspective: Dépendante de la croissance
                
                **🌾 Agriculture:**
                - Impact climatique croissant
                - Demande alimentaire structurelle
                - Perspective: Volatile mais haussière long terme
                """)
            
            with col2:
                st.markdown("""
                ### 📊 FACTEURS D'INFLUENCE
                
                **🌍 Géopolitique:**
                - Conflits au Moyen-Orient (pétrole)
                - Tensions commerciales USA-Chine
                - Sanctions internationales
                
                **📈 Macroéconomie:**
                - Politiques des banques centrales
                - Croissance des économies émergentes
                - Inflation et taux d'intérêt
                
                **🌦️ Climat:**
                - Événements El Niño/La Niña
                - Catastrophes naturelles
                - Changement climatique structurel
                
                **💡 Technologie:**
                - Énergies renouvelables
                - Véhicules électriques (demande cuivre, lithium)
                - Innovations agricoles
                """)
            
            st.markdown("""
            ### 🚨 RECOMMANDATIONS STRATÉGIQUES
            
            1. **Diversification:** Portefeuille équilibré entre énergies, métaux et agriculture
            2. **Couverture:** Utilisation d'options pour limiter le risque de baisse
            3. **Surveillance:** Monitoring des indicateurs géopolitiques et climatiques
            4. **Calendrier:** Attention aux rapports USDA, OPEP, et banques centrales
            5. **Liquidité:** Privilégier les commodités avec volumes de trading élevés
            6. **Horizon:** Adapter la stratégie à l'horizon de placement (court/moyen/long terme)
            """)
        
        # Rafraîchissement automatique
        if controls['auto_refresh']:
            time.sleep(10)  # Rafraîchissement toutes les 10 secondes
            st.rerun()

# Lancement du dashboard
if __name__ == "__main__":
    dashboard = CommodityDashboard()
    dashboard.run_dashboard()