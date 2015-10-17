import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';

import Rankings from '../components/Rankings';
import * as PlayersActions from '../actions/players';

class App extends Component {
  render() {
    // FIXME authentication!
    return (
      <div className="container">
        <nav className="navbar navbar-default" role="navigation">
          <div className="container-fluid">
            <ul className="nav navbar-nav nav-pills navbar-right">
              <li id="hypermeet">
                <a href=""><strong>HyperMeet 2015</strong></a>
              </li>
              <li id="about">
                <a href="">LieroGBG</a>
              </li>
              <li id="rankings">
                <a href="">Rankings</a>
              </li>
              <li id="rules">
                <a href="">Rules</a>
              </li>
              <li id="maps">
                <a href="">Maps</a>
              </li>
              <li id="administration">
                <a href="/admin">Administration</a>
              </li>
              <li id="logout">
                <a href="">Logout</a>
              </li>
              <li id="login">
                <a href="">Login</a>
              </li>
            </ul>
          </div>
        </nav>
        {this.props.children}
      </div>
    );
  }
}

App.PropTypes = {
  // FIXME add
};

export default App;
