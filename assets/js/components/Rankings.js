import React, { Component, PropTypes } from 'react';
import { map } from 'lodash/collection';

class Player extends Component {
  render() {
    const { season, player} = this.props;
    const pool_points = season(player).pp == 0 ? null :
      <span className="pool_points_remaining">
            (+{ season(player).pp } pool)
      </span>;
    const lives = season(player).lives > 0 ?
      <span className="change_positive">
        +{ season(player).lives }
      </span> :
      season(player).lives < 0 ?
        <span className="change_negative">
          { season(player).lives }
        </span> :
        <span>
          { season(player).lives }
        </span>;
    // FIXME add Liero worm image class here
    return (
      <tr>
        <td>{season(player).rank}</td>
        <td className="align_left">
          <img id={player.color}
               className="svg lieroworm lieroworm_right"
               src="/static/img/lieroworm_pointing_right.svg"></img>
          { player.name }
        </td>
        <td>
          <span className="rp_text">{ season(player).rp }</span>
          { pool_points }
        </td>
        <td>{ season(player).wins }</td>
        <td>{ season(player).losses }</td>
        <td>{ season(player).ties }</td>
        <td>{ season(player).matches }</td>
        <td>{ lives } </td>
        <td>
          <span className="rp_text">{ player.ante }</span>
        </td>
      </tr>
    );
  }
}

class Rankings extends Component {
  // FIXME re-add sorting functionality

  constructor(props) {
    super(props);
    this.state = {allTime: false };
  }

  componentWillMount() {
    this.props.actions.fetchPlayers();
  }

  render() {
    const { players } = this.props.players;
    var playerElems = map(players,
      p => <Player key={p.pk} player={p}
                   season={x => this.state.allTime ? x.allTime : x.season} />
    );
    return (
      <div className="row">
        <div className="col-xs-12">
          <table id="id_ranking_table"
                 className="table table-striped table-bordered">
            <thead>
              <tr>
                <th>#</th>
                <th className="align_left">Player</th>
                <th>Ranking points</th>
                <th>Wins</th>
                <th>Losses</th>
                <th>Ties</th>
                <th>Matches</th>
                <th>Lives</th>
                <th>Ante</th>
              </tr>
            </thead>
            <tbody>
              { playerElems }
            </tbody>
          </table>
        </div>
      </div>
    );
  }
}

Rankings.propTypes = {
  // FIXME this
};

export default Rankings;
