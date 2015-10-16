import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import Rankings from '../components/Rankings';
import * as PlayersActions from '../actions/players';

class App extends Component {
  render() {
    return <Rankings />
  }
}

App.PropTypes = {
  // FIXME add
};

// FIXME move into Rankings?
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
