import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from urllib.request import urlopen
import re

class DataExtractor:
    def __init__(self, season):
        self.season = season
        self.per_game_url = f"https://www.basketball-reference.com/leagues/NBA_{season}.html"
        self.standings_url = f"https://www.basketball-reference.com/leagues/NBA_{season}_standings.html"
        self.output_path = "extracted_data.csv"

    def scrape_per_game_stats(self):
        
        print(f"Scraping per-game stats for {self.season}")
        response = requests.get(self.per_game_url)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find('table', {'id': 'per_game-team'})

        if not table:
            raise ValueError(f"Per-game stats table not found for season {self.season}.")

        headers = [th.text for th in table.find('thead').find_all('th')][1:]
        rows = table.find('tbody').find_all('tr')
        data = []
        for row in rows:
            if row.get('class') and 'thead' in row.get('class'):
                continue
            data.append([td.text for td in row.find_all('td')])

        df = pd.DataFrame(data, columns=headers)
        df['Season'] = f"{self.season-1}/{self.season}"
       # df.to_csv("df.csv")
        return df

    def scrape_conference_standings(self):

        print(f"Scraping conference standings for {self.season}")
        response = requests.get(self.standings_url)
        soup = BeautifulSoup(response.text, "html.parser")

        conferences = ["E", "W"]
        standings_data = []

        for conference in conferences:
            table = soup.find('table', {'id': f"confs_standings_{conference}"})
            if not table:
                print(f"Standings table for {conference} conference not found. Skipping...")
                continue

            headers = [th.text for th in table.find('thead').find_all('th')]
            headers[0] = "Team"
            rows = table.find('tbody').find_all('tr')
            data = []
            for row in rows:
                if row.get('class') and 'thead' in row.get('class'):
                    continue
                team_name = row.find('th').text
                stats = [td.text for td in row.find_all('td')]
                team_data = [team_name] + stats
                data.append(team_data)

            df = pd.DataFrame(data, columns=headers)
            df['Conference'] = "East" if conference == "E" else "West"
            standings_data.append(df)

        standings_df = pd.concat(standings_data, ignore_index=True)
        standings_df['Season'] = f"{self.season-1}/{self.season}"
        #standings_df.to_csv("Standings_df.csv")
        return standings_df

    def scrape_advanced_stats(self):

        print(f"Scraping advanced stats for {self.season}...")
        table_html = BeautifulSoup(urlopen(self.per_game_url), "html.parser").findAll('table', id=re.compile('advanced-team'))[0]
        advanced_stats = pd.read_html(str(table_html))[0]
        advanced_stats.columns = advanced_stats.columns.droplevel(0)
        advanced_stats['Season'] = f"{self.season-1}/{self.season}"
        #advanced_stats.to_csv("advanced_stats_pipeline.csv")
        #print(advanced_stats)
        return advanced_stats

    def merge_datasets(self, per_game, standings, advanced):

        print("Merging datasets...")
        # Ensure proper merging columns
        per_game['Team'] = per_game['Team'].str.strip()
        standings['Team'] = standings['Team'].str.strip()
        advanced['Team'] = advanced['Team'].str.replace('*', '')
        advanced = advanced.rename(columns=lambda x: x.strip())
        standings['Team'] = standings['Team'].apply(lambda x: re.sub(r'\s*\(.*?\)', '', x).strip())
        #print(per_game.columns)
        #print(standings.columns)
        #print(advanced.columns)


        # Merge per-game stats with standings
        combined = pd.merge(per_game, standings, on=['Team', 'Season'], how='left')

        # Merge advanced stats
        final_combined = pd.merge(combined, advanced, on=['Team', 'Season'], how='left')
        #rint(final_combined.columns)
        final_combined["SRS"] = final_combined["SRS_y"]

        #required_columns = ["PW", "SRS", "NRtg", "ORtg", "TS%", "DRtg", "PA/G", "eFG%", "3P%", "FG%"]
        #missing_columns = [col for col in required_columns if col not in final_combined.columns]
        #print("Missing columns:", missing_columns)

        # Check for missing values in the required columns
        #missing_values = final_combined[required_columns].isnull().sum()
        #print("Missing values per column:", missing_values)

        return final_combined

    def extract(self):

        per_game_stats = self.scrape_per_game_stats()
        conference_standings = self.scrape_conference_standings()
        advanced_stats = self.scrape_advanced_stats()

        combined_data = self.merge_datasets(per_game_stats, conference_standings, advanced_stats)
        combined_data.to_csv(self.output_path, index=False)
        print(f"Data successfully saved to {self.output_path}.")
        return combined_data



if __name__ == "__main__":
    season = 2025
    extractor = DataExtractor(season)
    combined_data = extractor.extract()

    #print(combined_data.head())

