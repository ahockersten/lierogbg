import React, { Component, PropTypes } from 'react';

class Player extends Component {
  render() {
    return (
      <tr>
        <td>{this.props.player.rank}</td>
        <td className="align_left">
          <img id={this.props.player.color}
               className="svg lieroworm lieroworm_right"
               src="/static/img/lieroworm_pointing_right.svg"></img>
          { this.props.player.name }
        </td>
        <td>
          <span className="rp_text">{ this.props.player.rp }</span>
          <span className="pool_points_remaining">
            (+{ this.props.player.pp } pool)
          </span>
        </td>
        <td>{ this.props.player.wins }</td>
        <td>{ this.props.player.losses }</td>
        <td>{ this.props.player.ties }</td>
        <td>{ this.props.player.matches }</td>
        <td>
          <span className="change_positive">
            +{ this.props.player.lives }
          </span>
        </td>
        <td>
          <span className="rp_text">{ this.props.player.ante }</span>
        </td>
      </tr>
    );
  }
}

class Rankings extends Component {
  componentWillMount() {
    this.props.actions.fetchRankings();
  }

  render() {
    const { rankings } = this.props;
    var players = [];
    for (var i = 0; i < rankings.season.players.length; i++) {
      players.push(<Player key={rankings.season.players[i].pk}
                           player={rankings.season.players[i]}/>);
    }
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
              { players }
            </tbody>
          </table>
        </div>
      </div>
    );
  }
}

Rankings.propTypes = {
  // FIXME more specific types
  rankings: PropTypes.shape({
    season: PropTypes.object,
    alltime: PropTypes.object
  }).isRequired
};

export default Rankings;
