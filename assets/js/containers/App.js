import React, { Component, PropTypes } from 'react';
import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import bootstrap from 'bootstrap';

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
                <a href="/hypermeet2015">HyperMeet 2015</a>
              </li>
              <li id="about">
                <a href="/about">LieroGBG</a>
              </li>
              <li id="rankings">
                <a href="/rankings">Rankings</a>
              </li>
              <li id="rules">
                <a href="/rules">Rules</a>
              </li>
              <li id="maps">
                <a href="/maps">Maps</a>
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

export default App;
