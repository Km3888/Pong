# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import copy
import matplotlib.pyplot as plt

class Pong:
    class Player:
        def __init__(self,name,games):
            self.name=name
            self.games=games
            self.elo=1000
            self.high=1000
            self.low=1000
            
        def update_elo(self,diff,won,exp):
            if diff>0 or not(won):
                self.elo+=diff*32
            if self.elo>self.high:
                self.high=self.elo
            elif self.elo<self.low:
                self.low=self.elo
    class Game:
        def __init__(self,date,player1,player2,score,points,winner,gametype):
            self.date=date
            self.player1=player1
            self.player2=player2
            self.score=score
            self.points=points
            self.winner=(self.player1 if winner else self.player2)
            self.type=int(gametype)
            
    def __init__(self,df=None,csv=None):
        if df is None:
            if csv is None:
                raise ValueError('must have input')
            else:
                self.df=pd.read_csv(csv)
        else:
            self.df=df  #df is a datframe object
        self.clean_ommissions()
        if isinstance(self.df.iloc[0]['Date'],str):
            self.clean_date()
        self.clean_columns() #fills all missing values with most recent nonnull value
        self.add_winner() #creates new column which indicates whether Player 1 won
        self.add_margin() #creates a new column which indicates the absolute difference between the two players' scores
        self.players=[] # Code from here downwards just creates a list of Player objects which store the player's
        self.player_dict={} #name, elo ranking, and a list of all the games in which they've participated
        u=self.df['Player 1 - Name'].unique()#The dictionary allows us to get the player object from a string of the player's name
        s=set(self.df['Player 1 - Name'].unique()).union(set(self.df['Player 2 - Name'].unique()))
        for player in list(s):
            #self.games.append(Game(self.))'
            a=self.Player(player,self.games(self.player_df(player)))
            self.player_dict[player]=a
            self.players.append(a)
            
    #Initializer helper functions
    def add_margin(self):
        if 'Margin' not in self.df.columns:
            self.df['Margin']=abs(self.df['Player  1 - Score']-self.df['Player 2 - Score'])
        
    def add_winner(self):
        if 'Won' not in self.df.columns:
            self.df['Won?']=self.df['Player  1 - Score']>self.df['Player 2 - Score']
        
    def clean_date(self):
        for row in range(self.df.shape[0]):
            og_date=self.df.loc[row]['Date'].split('/')
            date=[]
            for x in og_date:
                if len(x)==2:
                    date.append(x)
                else:
                    date.append('0'+x)
            new_date=''.join([date[2],date[0],date[1]])
            self.df.at[row,'Date']=int(new_date)
    
    def clean_ommissions(self):
        for column in self.df.columns:
            for row in range(self.df.shape[0]):
                if pd.isnull(self.df.iloc[row][column]):
                    self.df.at[row,column]=self.df.iloc[row-1][column]
                    
    def clean_columns(self):
        accepted_columns=['Date', 'Player 1 - Name', 'Player  1 - Score', 'Player 2 - Name','Player 2 - Score', 'Game Type(11 or 21)','Won?', 'Margin']
        for column in self.df.columns:
            if column not in accepted_columns:
                del self.df[column]
        
    def games(self,df=None):
        if df is None:
            df=self.df
        games=[]
        for row in range(df.shape[0]):
            Date=df.iloc[row]['Date']
            Player1=df.iloc[row]['Player 1 - Name']
            Player2=df.iloc[row]['Player 2 - Name']
            Score=[df.iloc[row]['Player  1 - Score'],df.iloc[row]['Player 2 - Score']]
            Points=df.iloc[row]['Game Type(11 or 21)']
            won=df.iloc[row]['Won?']
            t=df.iloc[row]['Game Type(11 or 21)']
            games.append(self.Game(Date,
                                   [Player1],
                                   [Player2],
                                   Score,Points,won,t))
        return games
        
    def players(self):
        return pd.unique(self.df[['Player 1 - Name','Player 2 - Name']].values.ravel('K'))
        
        #Creates a new dataframe including only the games in which the specified player has participated
    def player_df(self,player,df=None):
        if df is None:
            df=self.df
        #Takes a subset of the dataframe to get all games where player is player 1
        a=df.loc[df['Player 1 - Name']==player,:]
        #Takes a subset of the dataframe to get all the games where player is player 2
        b=df.loc[df['Player 2 - Name']==player,:]
        #All this code just reformats the games in b so that player 1 is player 1
        c=pd.DataFrame()
        c['Date']=b['Date']
        c['Player 1 - Name']=b['Player 2 - Name']
        c['Player  1 - Score']=b['Player 2 - Score']
        c['Player 2 - Name']=b['Player 1 - Name']
        c['Player 2 - Score']=b['Player  1 - Score']
        c['Game Type(11 or 21)']=b['Game Type(11 or 21)']
        c['Won?']=[not b.iloc[x]['Won?'] for x in range(b.shape[0])]
        c['Margin']=b['Margin']
        #put a and the modified b together and returns it
        output=pd.concat([a,c])
        
        return output
        
    #returns a dataframe of all the games played by two players within a given date range
    def matchup_df(self,player1,player2,df=None,date = None):
        if df is None:
            df=self.df
        if isinstance(date,list):
            df=df.loc[df['Date']>date[0],:]
            df=df.loc[df['Date']<date[1],:]
        if isinstance(date,int):
            df=df.loc[df['Date']>date,:]
        a=self.player_df(player1,df=df)        
        return a.loc[a['Player 2 - Name']==player2,:]
        
    #Generates a dataframe with information about the games played between two players
    def matchup_report(self,player1,player2,df=None,date=None):
        #a is the dataframe of all the games where player 1 is listed as player 2 and vice versa
        #b is the dataframe of all the games where player 1 and player 2 are both listed as such
        a=self.matchup_df(player1,player2,df,date)
        if date is not None:
            a=a.loc[a['Date']>date,:]
        player_1_points=a['Player  1 - Score'].sum()
        player_2_points=a['Player 2 - Score'].sum()
        player_1_wins=a['Won?'].sum()
        player_2_wins=a.shape[0]-player_1_wins
        total_games=a.shape[0]
        results={'Players':[player1,player2],
                 'Total games':[total_games,total_games],
                 'Points':[player_1_points,player_2_points],
                 'Wins':[player_1_wins,player_2_wins]}
        return pd.DataFrame(results)
    
    #Generates a dataframe of all the games played by a list of players
    def group_df(self,group):
        a=copy.deepcopy(self.df)
        players=[self.player_dict[x] for x in group]
        not_players=[x for x in self.players if x not in players]
        for p in not_players:
            name=p.name
            a=a.loc[a['Player 1 - Name']!=name,:]
            a=a.loc[a['Player 2 - Name']!=name,:]
        return a
#=============================================================Stats stuff
    def factorial(self,n):#pretty self-explanatory
        if n==1 or n==0:
            return 1
        else:
            return n*self.factorial(n-1)
            
    def combinations(self,n,k):#formula for combinations
        return self.factorial(n)/(self.factorial(k)*(self.factorial(n-k)))
    
    def binomial_prob(self,n,k,p):
        #odds of an event with probability p occuring k times out of n trials
        return self.combinations(n,k)*(p**k)*(1-p)**(n-k)
    
    def point_ratio_to_win_prob(self,p,k):
        #Odds of a player winning a game to k points if their probability of winning an
        #individual point is p
        #p is odds of winning one game
        #k is how many points the game is out of
        n=(k-1)*2
        win_prob=0
        for x in range(k,n+1):
            win_prob+=self.binomial_prob(n,x,p)
        odds_of_winning_deuces=p**2/(1-2*p*(1-p))
        win_prob+=odds_of_winning_deuces*self.binomial_prob(n,k-1,p)
        return win_prob
        
    def win_prob_to_ratio(self,p):
        return p/(1-p)
        
    def calc_elo_ratings(self):
        for game in self.games():
            
            #gets the elo rating of each player
            p1=self.player_dict[game.player1[0]]
            p2=self.player_dict[game.player2[0]]
            
            
            #calculates the expected probability of each player beating the other based on elo ratings
            expected1=1/(1 + 10 **((p2.elo - p1.elo)/400))
            expected2=1/(1 + 10 **((p1.elo - p2.elo)/400))
            
            #Finds the probability of each player beating the
            #other based on the point differential for their game
            actual1=self.point_ratio_to_win_prob(game.score[0]/(game.score[0]+game.score[1]),game.type)
            actual2=self.point_ratio_to_win_prob(game.score[1]/(game.score[0]+game.score[1]),game.type)
            
            diff1=(actual1-expected1)
            diff2=(actual2-expected2)
            
            #Normalizes difference in case of tight game
            if game.score[0]>=game.type-1 and game.score[1]>=game.type-1:
                diff1=diff1/2
                diff2=diff2/2
            elif abs(game.score[0]-game.score[1])==2:
                diff1=diff1/1.3
                diff2=diff2/1.3
            elif abs(game.score[0]-game.score[1])==1:
                diff1=2*diff1
                diff2=2*diff2
            
            #green portion allows you to check how the elo
            #gets updated if you uncomment
            
            print('================================')
            print('Names:',p1.name,p2.name)
            print('elos:',p1.elo,p2.elo)
            print('expected:',expected1,expected2)
            print('point_prob:',actual1,actual2)
            print('score:',game.score[0],game.score[1])
            print('diff=',diff1,diff2)
            #calls method of the player class to update elo scores in light
            #of new game
            p1.update_elo(diff1,game.score[0]>game.score[1],expected1)
            p2.update_elo(diff2,game.score[0]<game.score[1],expected2)
            print('new_elos:',p1.elo,p2.elo)
            

    #sorts players by their elo rating to rank them in order
    #(yes I used bubble sort, sue me)
    def elo_rankings(self):
        self.calc_elo_ratings()
        for i in range(len(self.players)):
            swapped=False
            for j in range(len(self.players)-i-1):
                if self.players[j].elo<self.players[j+1].elo:
                    self.players[j],self.players[j+1]=self.players[j+1],self.players[j]
                    swapped=True
            if not swapped:
                break
        ranks=[x+1 for x in range(len(self.players))]
        names=[x.name for x in self.players]
        scores=[x.elo for x in self.players]
        d={'Rank':ranks,'Name':names,'Rating':scores}
        return d
        #returns a dictionary
        
    def ranking_df(self):#converts elo_rankings dictionary into dataframe for presentation
        return pd.DataFrame(self.elo_rankings())
        
    
    def print_by_date(self):
        nums={}
        for player in self.players:
            nums[player.name]=[1000]
        for date in self.df['Date'].unique():
            a=self.df.loc[self.df['Date']<=int(date),:]
            d=self.elo_rankings()
            names=d['Name']
            scores=d['Rating']
            for j in range(len(names)):
                name=names[j]
                score=scores[j]
                if name not in nums:
                    nums[name]=[score]
                else:
                    nums[name].append(score)
        for name in nums.keys():
            plt.plot(nums[name])
        plt.show()
        
    def is_valid(self):
        #Checks whether every player in the dataframe has at least 20 games against players in
        #the dataframe, if not then it returns a dictionary of all who don't have 20 and how 
        #many they do have
        b=True
        invalids={}
        for player in self.players:
            if len(player.games)<20:
                b=False
                invalids[player.name]=len(player.games)
        if b:
            return True
        else:
            return invalids
        
    def test(self):#checks how elo rankings change over time to find bugs
        nums={}
        for player in self.players:
            nums[player.name]=[1000]
        for i in range(5):
            print('=============================')
            print('NEW ITERATION')
            print('=============================')
            d=self.elo_rankings()
            names=d['Name']
            scores=d['Rating']
            for j in range(len(names)):
                name=names[j]
                score=scores[j]
                if name not in nums:
                    nums[name]=[score]
                else:
                    nums[name].append(score)
        for name in nums.keys():
            plt.plot(nums[name])
        plt.show()
            
            
            
today=r'/Users/km3888/Desktop/Pong.csv'
everyone=Pong(csv=today)
a=everyone.df
players=['Kelly','Kende','Nate','Jack','Emilio','Hank','Kohei','Chris']#'Hank','Chris','Stefano','Emilio','Kohei']
df=everyone.group_df(players)
new=Pong(df=df)
#print(new.elo_rankings())
#print(new.print_by_date())
print(new.ranking_df())
a=new.matchup_df('Kelly','Kende')