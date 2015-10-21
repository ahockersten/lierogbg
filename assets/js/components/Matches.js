import React, { Component } from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import _ from 'lodash';

import * as MatchesActions from '../actions/matches';
import { RankingPointsChange } from './RankingPointsChange';
import { Spinner } from './Spinner';
import { TableHeader } from './TableHeader';
import { WormImageLeft, WormImageRight } from './WormImage';

class Round {
  render() {
    const { round, index } = this.props;
    return (
      <tr>
        <td>Round {index}</td>
        <td>{round.map}</td>
        <td>
          <WormImageRight color={round.player_left.color} />
          {round.player_left.lives} ‒ {round.player_right.lives}
          <WormImageLeft color={round.player_right.color} />
        </td>
        <td>
          {round.file ?
            <a href="{r.file}">
              <span className="glyphicon glyphicon-save"></span>
            </a> : ""}
        </td>
      </tr>
    );
  }
}


class MatchDetails extends Component {
  render() {
    return (
      <td colspan="6">
        <div className="panel panel-info">
          <div className="panel-body">
            <table className="table table-striped">
              <thead>
                <tr>
                  <th>Round</th>
                  <th>Map</th>
                  <th>Score</th>
                  <th>Download</th>
                </tr>
              </thead>
              <tbody>
                {_.map(this.props.rounds,
                       (r,i) => <Round key={r.pk} round={r} index={i} />)}
              </tbody>
            </table>
          </div>
        </div>
      </td>
    );
  }
}

class MatchSummary extends Component {
  render() {
    const { match } = this.props
    return (
      <tr className="match-simple">
        <td>{match.start_time}</td>
        <td className="align_left">
          <WormImageRight color={match.player_left.color} />
          {match.player_left.name}
        </td>
        <td>
          {match.player_left.rp_after} <RankingPointsChange rp_change={match.player_left.rp_change} />
        </td>
        <td className="align_left">
          <WormImageLeft color={match.player_right.color} />
          {match.player_right.name}
        </td>
        <td>
          {match.player_right.rp_after } <RankingPointsChange rp_change={match.player_right.rp_change} />
        </td>
        <td>{match.winner.name}</td>
        <td>{match.type}</td>
      </tr>
    );
  }

}

class Match extends Component {
  constructor(props) {
    super(props);
    this.state = {
      detailed: false
    };
    this.changeDetail = this.changeDetail.bind(this);
  }

  changeDetail() {
    this.setState({detailed: !this.state.detailed});
  }

  render() {
    return (
        <MatchSummary onClick={this.changeDetail} match={this.props.match}>
          {this.state.detailed ? <MatchDetails match={this.props.match} /> : ""};
        </MatchSummary>
    );
  }
}

class Matches extends Component {
  constructor(props) {
    super(props);
    this.state = {
      sortBy: 'time',
      sortOrder: 'desc'
    };
    this.loadMore = this.loadMore.bind(this);
  }

  componentWillMount() {
    this.props.actions.fetchMatches();
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
      if (sortBy == 'time') {
        this.setState({sortOrder: 'desc'});
      }
      else {
        this.setState({sortOrder: 'asc'});
      }
    }
  }

  loadMore() {
    // FIXME load more matches from server here
  }

  render() {
    // FIXME sorting doesn't do anything
    return (
      <div className="row">
        <div className="col-xs-12">
          <table className="table" id="id_list_matches_table">
            <thead>
              <tr>
                <TableHeader name='Time' sorter='time'
                             sortBy={this.state.sortBy}
                             sortOrder={this.state.sortOrder}
                             changeSorting={this.changeSorting} />
                <TableHeader name='Left player' sorter='left_player'
                             cssClasses={['align_left']}
                             sortBy={this.state.sortBy}
                             sortOrder={this.state.sortOrder}
                             changeSorting={this.changeSorting} />
                <TableHeader name='Left player RP' sorter='left_player_rp'
                             sortBy={this.state.sortBy}
                             sortOrder={this.state.sortOrder}
                             changeSorting={this.changeSorting} />
                <TableHeader name='Right player' sorter='right_player'
                             cssClasses={['align_left']}
                             sortBy={this.state.sortBy}
                             sortOrder={this.state.sortOrder}
                             changeSorting={this.changeSorting} />
                <TableHeader name='Right player RP' sorter='right_player_rp'
                             sortBy={this.state.sortBy}
                             sortOrder={this.state.sortOrder}
                             changeSorting={this.changeSorting} />
                <TableHeader name='Winner' sorter='winner'
                             sortBy={this.state.sortBy}
                             sortOrder={this.state.sortOrder}
                             changeSorting={this.changeSorting} />
                <TableHeader name='Match type' sorter='type'
                             sortBy={this.state.sortBy}
                             sortOrder={this.state.sortOrder}
                             changeSorting={this.changeSorting} />
              </tr>
            </thead>
            <tbody>
              {_.map(this.props.matches.matches,
                     m => <Match key={m.pk} match={m} />)}
            </tbody>
          </table>
        </div>
        <div className="col-xs-12">
          <button type="button" className="btn btn-block"
                  onClick={this.loadMore}>
            Load more...
          </button>
        </div>
      </div>
    );
  }
}

function mapStateToProps(state) {
  return {
    matches: state.matches
  };
}

function mapDispatchToProps(dispatch) {
  return {
    actions: bindActionCreators(MatchesActions, dispatch)
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(Matches);
