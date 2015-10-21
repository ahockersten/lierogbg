import React, { Component } from 'react';

export class Rules extends Component {
  render() {
    return (
      <div className="row">
        <div className="col-xs-12">
          <h2>Rules</h2>
          <h3>Settings</h3>

          <p>
            <ul>
              <li>Game Mode: <em>Kill 'em All</em></li>
              <li>Lives: <em>8</em></li>
              <li>Loading Times: <em>20%</em></li>
              <li>Replays: <em>ON</em></li>
              <li>Bonuses: <em>None</em></li>
              <li>Map: <em>ON</em></li>
              <li>Load+Change: <em>ON</em></li>
              <li>Player Health: <em>100%</em></li>
              <li>Weapon Options: <em>No bans</em></li>
            </ul>
          </p>

          <h3>Ranking Points</h3>

          <p>
            In order to calculate relative skill levels between players located
            in many different places we use a version of the Elo rating system
            similar to that used in competitive chess. The difference in ranking
            points (RP) between two players serves as a predictor of the
            outcome of the game, and the player with the higher rank will have
            more to lose in the event of a loss. If all players win equally
            much, their RP will stabilize at around 1000, as 1000 points is
            introduced into the system successively for every player that
            joins it.
          </p>
          <p>
            So as not to have new players jump straight up to 1000 RP and
            overtake half of the players on the list, players unlock their
            points from an individual pool (40 points for every 1v1 game and a
            varied amount for tournaments) as more games are played.
          </p>
          <p>
            Before a match/tournament begins, the proper amount of points
            (as long as there are any left) are taken from each player's pool
            and added to their RP. Then an amount of that total is bet as ante
            in the match/tournament and given to the winner(s) once completed.
          </p>
          <p>
            That amount is calculated by by the following formula:<br/>
                (RP² / 1000) * x<br/>
            where x is the ante percentage of that match/tournament:<br/>
                2% for a match<br/>
                2-5% for a tournament<br/>
          </p>
          <p>
            For a regular match this means that players with 1000 RP bets an
            ante of 20 RP, players below that bets exponentially less and
            players above that bets exponentially more (i.e. a player with
            1200 bets 29, one at 1500 bets 45, one at 800 bets 13 and one at
            500, 5).
          </p>
        </div>
      </div>
    );
  }
}

export default Rules;
