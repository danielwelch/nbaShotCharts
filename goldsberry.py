import matplotlib.pyplot as plt
import numpy as np
import nbaShotCharts as nba
import argparse


def get_nba_avg(df, basic, area, range):
    '''Returns the NBA average FG percentage for a zone
     on the court, defined by the basic, area, and range
     parameters as per stats.nba.com API. Requires pandas
     data frame with NBA Average data, like the one returned
     by nbaShotCharts.py get_league_avg method in Shots class
     '''
    result = df.loc[(
        df["SHOT_ZONE_BASIC"] == basic) & (
        df["SHOT_ZONE_AREA"] == area) & (
        df["SHOT_ZONE_RANGE"] == range),
        "FG_PCT"
    ].values

    if len(result) == 1:
        return result[0]
    else:
        raise IndexError  # replace with custom error


def two_or_three(basic):
    three_zones = [
        "Backcourt", "Above the Break 3", "Left Corner 3", "Right Corner 3"
    ]
    two_zones = [
        "In The Paint (Non-RA)", "Mid-Range", "Restricted Area"
    ]
    if basic in three_zones:
        return 3.
    elif basic in two_zones:
        return 2.
    else:
        raise IndexError  # replace with custom error


def expected_points_scored(points, avg_fg_pct):
    return points * avg_fg_pct


def expected_points_scored_row(row, avg_df):
    '''Accepts row from pandas dataframe, calls points_scored given
    necessary args from row, and returns integer result of
    expected_points_scored. avg_df is a dataframe of nba averages
    from each shot zone, obtained here from nbaShotCharts.py
    '''
    return expected_points_scored(
        points=two_or_three(row["SHOT_ZONE_BASIC"]),
        avg_fg_pct=get_nba_avg(
            df=avg_df,
            basic=row["SHOT_ZONE_BASIC"],
            area=row["SHOT_ZONE_AREA"],
            range=row["SHOT_ZONE_RANGE"]
        )
    )


def points_scored(basic, made):
    if made is 0:
        return 0.
    else:
        return two_or_three(basic)


def points_scored_row(row):
    '''Accepts row from pandas dataframe, calls points_scored given
    necessary args from row, and returns integer result of points_scored
    '''
    return points_scored(row["SHOT_ZONE_BASIC"], row["SHOT_MADE_FLAG"])


def add_points_scored(df):
    '''Returns a pandas dataframe with a new column - POINTS_SCORED -
    for each shot in the original player shot chart dataframe.
    '''
    df["POINTS_SCORED"] = df.apply(points_scored_row, axis=1)
    return df


def add_expected_points_scored(df, avg_df):
    '''Returns a pandas dataframe with a new column - EXPECTED_POINTS_SCORED -
    for each shot in the original player shot chart dataframe.
    avg_df is a dataframe of nba average from each shot zone,
    obtained here from nbaShotCharts.py
    '''
    df["EXPECTED_POINTS_SCORED"] = df.apply(
        expected_points_scored_row, axis=1, args=(avg_df,)
    )
    return df


def goldsberry(player_name, hex_gridsize=30, cmap=plt.cm.coolwarm, joint=False):
    player = nba.Shots(nba.get_player_id(player_name))
    nba_avg = player.get_league_avg()
    player_sc = add_expected_points_scored(
        add_points_scored(
            player.get_shots()
        ), nba_avg
    )

    plt.figure(figsize=(12, 11))
    nba.draw_court(outer_lines=True)

    if joint:
        pass
    else:
        nba.shot_chart(
            x=player_sc.LOC_X, y=player_sc.LOC_Y, kind="hex",
            C=np.divide(player_sc.POINTS_SCORED, player_sc.EXPECTED_POINTS_SCORED),
            hex_gridsize=hex_gridsize,
            cmap=cmap,
        )

    plt.xlim(-300, 300)
    plt.ylim(-100, 500)
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create goldsberry-like nba shot charts')
    parser.add_argument(
        '--player', type=str,
        default="James, LeBron",
        help="player name in 'Last, First' format"
    )
    parser.add_argument(
        '--hex_gridsize', type=int,
        default=30,
        help="hex gridsize for matplotlib"
    )

    args = parser.parse_args()
    goldsberry(args.player)
