import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import _ from 'lodash';

import * as PlayersActions from '../actions/players';
import { Lives } from './Lives';
import { PoolPoints } from './PoolPoints';
import { Spinner } from './Spinner';
import { TableHeader } from './TableHeader';
import { WormImageRight } from './WormImage';

class Player extends Component {
  render() {
    const { season, player, total_players} = this.props;
    return (
      <tr>
        <td>{player.rank == total_players ? '-' : player.rank}</td>
        <td className="align_left">
          <WormImageRight color={player.color} />
          { player.name }
        </td>
        <td>
          <span className="rp_text">{ player.rp }</span>
          <PoolPoints pp={player.pp} />
        </td>
        <td>{ player.wins }</td>
        <td>{ player.losses }</td>
        <td>{ player.ties }</td>
        <td>{ player.matches }</td>
        <td>
          <Lives lives={player.lives} />
        </td>
        <td>
          <span className="rp_text">{ player.ante }</span>
        </td>
      </tr>
    );
  }
}


class RankingTable extends Component {
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
        .map(p => <Player key={p.pk} player={p}
                          total_players={this.props.players.players.length} />)
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
      <div className="row">
        <div className="col-xs-12">
          <div className="dropdown">
            <button type="button" className="btn btn-default dropdown-toggle"
                    data-toggle="dropdown" aria-haspopup="true"
                    aria-expanded="false">
              Show <span className="caret"></span>
            </button>
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
          </div>
        </div>
        <div className="col-xs-12">
          {content}
        </div>
      </div>
    );
  }
}
RankingTable.propTypes = {
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

export default connect(mapStateToProps, mapDispatchToProps)(RankingTable);
