import React, { Component, PropTypes } from 'react';

class Rankings extends Component {
  // FIXME use <Link> here and elsewhere
  render() {
    return (
      <div>
        <div id="sub_menu" className="navbar" role="navigation">
          <ul className="nav nav-pills navbar-left">
            <li id="add_game">
              <a href="">Add match</a>
            </li>
            <li id="add_tournament">
              <a href="">Add tournament</a>
            </li>
          </ul>
          <ul className="nav nav-pills navbar-right">
            <li id="ranking" >
              <a href="/rankings">Ranking</a>
            </li>
            <li id="matches" >
              <a href="/rankings/matches">Matches</a>
            </li>
            <li id="tournaments" >
              <a href="/rankings/tournaments">Tournaments</a>
            </li>
          </ul>
        </div>
        <div className="content">
          {this.props.children}
        </div>
      </div>
    );
  }
}

export default Rankings;
