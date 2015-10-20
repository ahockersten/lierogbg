import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import _ from 'lodash';

import * as PlayersActions from '../actions/players';
import { WormImageRight } from './WormImage';
import { Spinner } from './Spinner';

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


class TableHeader extends Component {
  render() {
    var classes;
    var sortSymbol = "";
    if (this.props.sorter == this.props.sortBy) {
      classes = _.reduce(this.props.cssClasses, function(acc, n) {
        return acc + ", " + n;
      }, "sorter");
      sortSymbol = this.props.sortOrder == 'asc' ? '▼' : '▲';
    }
    else {
      classes = _.reduce(this.props.cssClasses, function(acc, n) {
        return acc + ", " + n;
      });
    }
    return (
      <th className={classes}
          onClick={this.props.changeSorting.bind(null, this.props.sorter)}>
        {this.props.name} {sortSymbol}
      </th>
    );
  }
}
TableHeader.propTypes = {
  // the externally visible name to put on this header
  name: PropTypes.string.isRequired,
  // additional css classes for this
  cssClasses: PropTypes.arrayOf(PropTypes.string),
  // the player property to use for sorting
  sorter: PropTypes.string.isRequired,
  // the player property currently being used for sorting
  sortBy: PropTypes.string.isRequired,
  // the current sorting order, 'asc' or 'desc'
  sortOrder: PropTypes.string.isRequired,
  // function to call to change the sorting
  changeSorting: PropTypes.func.isRequired
};
TableHeader.defaultProps = {
  cssClasses: []
};


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

  render() {
    var content;
    if (this.props.players.isFetching) {
      content = <Spinner />
    }
    else {
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
      content = (
        <table id="id_ranking_table"
               className="table table-striped table-bordered table-sortable">
          <thead>
            <tr>
              <TableHeader name='#' sorter='rank'
                           sortBy={this.state.sortBy}
                           sortOrder={this.state.sortOrder}
                           changeSorting={this.changeSorting} />
              <TableHeader name='Player'
                           cssClasses={['align_left']} sorter='name'
                           sortBy={this.state.sortBy}
                           sortOrder={this.state.sortOrder}
                           changeSorting={this.changeSorting} />
              <TableHeader name='Ranking points' sorter='rp'
                           sortBy={this.state.sortBy}
                           sortOrder={this.state.sortOrder}
                           changeSorting={this.changeSorting} />
              <TableHeader name='Wins' sorter='wins'
                           sortBy={this.state.sortBy}
                           sortOrder={this.state.sortOrder}
                           changeSorting={this.changeSorting} />
              <TableHeader name='Losses' sorter='losses'
                           sortBy={this.state.sortBy}
                           sortOrder={this.state.sortOrder}
                           changeSorting={this.changeSorting} />
              <TableHeader name='Ties' sorter='ties'
                           sortBy={this.state.sortBy}
                           sortOrder={this.state.sortOrder}
                           changeSorting={this.changeSorting} />
              <TableHeader name='Matches'
                           sorter='matches'
                           sortBy={this.state.sortBy}
                           sortOrder={this.state.sortOrder}
                           changeSorting={this.changeSorting} />
              <TableHeader name='Lives' sorter='lives'
                           sortBy={this.state.sortBy}
                           sortOrder={this.state.sortOrder}
                           changeSorting={this.changeSorting} />
              <TableHeader name='Ante' sorter='ante'
                           sortBy={this.state.sortBy}
                           sortOrder={this.state.sortOrder}
                           changeSorting={this.changeSorting} />
            </tr>
          </thead>
          <tbody>
            { players }
          </tbody>
        </table>
      );
    }
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
              {content}
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
