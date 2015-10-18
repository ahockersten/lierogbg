import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import _ from 'lodash';
import bootstrap from 'bootstrap';

import * as PlayersActions from '../actions/players';

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
    this.state = {
      allTime: false,
      inactive: false
    };
    this.inactivePlayersChanged = this.inactivePlayersChanged.bind(this);
    this.allTimeChanged = this.allTimeChanged.bind(this);
  }

  componentWillMount() {
    this.props.actions.fetchPlayers();
  }

  inactivePlayersChanged(event) {
    this.setState({inactive: event.target.checked});
  }

  allTimeChanged(event) {
    this.setState({allTime: event.target.checked});
  }

  render() {
    let players = _(this.props.players.players)
      .filter(p => this.state.inactive ? p : p.active)
      .map(p => <Player key={p.pk} player={p}
                        season={x => this.state.allTime ? x.allTime : x.season} />)
      .value();
    // FIXME check authentication
    return (
      <div>
        <div id="sub_menu" className="navbar" role="navigation">
          <ul className="nav nav-pills navbar-left">
            <li className="dropdown">
              <a className="dropdown-toggle" id="show" data-toggle="dropdown">
                Show <span className="caret"></span>
              </a>
              <ul className="dropdown-menu" role="menu">
                <li role="presentation">
                  <label role="menu-item">
                  <input type="checkbox" onChange={this.inactivePlayersChanged}
                         value={this.state.inactive}
                         id="inactive-players-checkbox"/>
                    Inactive players
                  </label>
                  <label role="menu-item">
                  <input type="checkbox" onChange={this.allTimeChanged}
                         value={this.state.allTime}
                         id="all-time-checkbox"/>
                    All time
                  </label>
                </li>
              </ul>
            </li>
            <li id="add_game">
              <a href="">Add match</a>
            </li>
            <li id="add_tournament">
              <a href="">Add tournament</a>
            </li>
          </ul>
          <ul className="nav nav-pills navbar-right">
            <li id="ranking" >
              <a href="">Ranking</a>
            </li>
            <li id="games" >
              <a href="">Matches</a>
            </li>
            <li id="tournaments" >
              <a href="">Tournaments</a>
            </li>
          </ul>
        </div>
        <div className="content">
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
        </div>
      </div>
    );
  }
}

Rankings.propTypes = {
  // FIXME this
};

function mapStateToProps(state) {
  return {
    players: state.players
  };
}

function mapDispatchToProps(dispatch) {
  return {
    actions: bindActionCreators(PlayersActions, dispatch)
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(Rankings);
