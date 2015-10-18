import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import _ from 'lodash';

import * as PlayersActions from '../actions/players';
import { WormImageRight } from './WormImage';

class Player extends Component {
  render() {
    const { season, player} = this.props;
    const pool_points = player.pp == 0 ? null :
      <span className="pool_points_remaining">
        (+{ player.pp } pool
      </span>;
    const lives = player.lives > 0 ?
      <span className="change_positive">
        +{ player.lives }
      </span> :
      player.lives < 0 ?
        <span className="change_negative">
          { player.lives }
        </span> :
        <span>
          { player.lives }
        </span>;
    // FIXME add Liero worm image class here
    return (
      <tr>
        <td>{player.rank}</td>
        <td className="align_left">
          <WormImageRight color={player.color} />
          { player.name }
        </td>
        <td>
          <span className="rp_text">{ player.rp }</span>
          { pool_points }
        </td>
        <td>{ player.wins }</td>
        <td>{ player.losses }</td>
        <td>{ player.ties }</td>
        <td>{ player.matches }</td>
        <td>{ lives } </td>
        <td>
          <span className="rp_text">{ player.ante }</span>
        </td>
      </tr>
    );
  }
}

class Rankings extends Component {
  constructor(props) {
    super(props);
    this.state = {
      allTime: false,
      inactive: false,
      sortBy: 'rank',
      sortOrder: 'asc'
    };
    this.inactivePlayersChanged = this.inactivePlayersChanged.bind(this);
    this.allTimeChanged = this.allTimeChanged.bind(this);
    this.changeSorting = this.changeSorting.bind(this);
    this.createTableHeader = this.createTableHeader.bind(this);
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

  changeSorting(sortBy) {
    if (this.state.sortBy == sortBy) {
      if (this.state.sortOrder == 'asc') {
        this.setState({sortOrder: 'desc'});
      }
      else {
        this.setState({sortOrder: 'asc'});
      }
    }
    else {
      this.setState({sortBy: sortBy});
      this.setState({sortOrder: 'asc'});
    }
  }

  // FIXME this could be its own element
  createTableHeader(name, classes, sortBy) {
    if (sortBy == this.state.sortBy) {
      return (
        <th className={"sortBy " + classes}
            onClick={this.changeSorting.bind(this, sortBy)}>
          {name} {this.state.sortOrder == 'asc' ? '▼' : '▲'}
        </th>
      );
    }
    else {
      return (
        <th className={classes}
            onClick={this.changeSorting.bind(this, sortBy)}>
          {name}
        </th>
      );
    }
  }

  render() {
    let flatPlayers =
      _.map(this.props.players.players,
            p => _.merge(_.omit(p, 'season', 'allTime'),
                         this.state.allTime ? p.allTime : p.season));
    let players = _(flatPlayers)
      .filter(p => this.state.inactive ? p : p.active)
      .sortByOrder(this.state.sortBy, this.state.sortOrder)
      .map(p => <Player key={p.pk} player={p} />)
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
                     className="table table-striped table-bordered table-sortable">
                <thead>
                  <tr>
                    {this.createTableHeader('#', '', 'rank')}
                    {this.createTableHeader('Player', 'align_left', 'name')}
                    {this.createTableHeader('Ranking points', '', 'rp')}
                    {this.createTableHeader('Wins', '', 'wins')}
                    {this.createTableHeader('Losses', '', 'losses')}
                    {this.createTableHeader('Ties', '', 'ties')}
                    {this.createTableHeader('Matches', '', 'matches')}
                    {this.createTableHeader('Lives', '', 'lives')}
                    {this.createTableHeader('Ante', '', 'ante')}
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
