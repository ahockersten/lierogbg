import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import Rankings from '../components/Rankings';
import * as RankingsActions from '../actions/rankings';

class App extends Component {
  render() {
    return <Rankings />
  }
}

App.PropTypes = {
  // FIXME add
};

function mapStateToProps(state) {
  return {
    rankings: state.rankings
  };
}

function mapDispatchToProps(dispatch) {
  return {
    actions: bindActionCreators(RankingsActions, dispatch)
  }
}

export default connect(mapStateToProps, mapDispatchToProps)(Rankings);
