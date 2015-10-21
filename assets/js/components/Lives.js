import React, { Component } from 'react';

export class Lives extends Component {
  render() {
    if (this.props.lives > 0) {
      return (
        <span className="change_positive">
          +{ this.props.lives }
        </span>
      );
    }
    else if (this.props.lives == 0) {
      return (
        <span>
          { this.props.lives }
        </span>
      );
    }
    else {
      return (
        <span className="change_negative">
          { this.props.lives }
        </span>
      );
    }
  }
}

export default Lives;
