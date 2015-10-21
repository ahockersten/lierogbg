import React, { Component } from 'react';

export class PoolPoints extends Component {
  render() {
    if (this.props.pp == 0) {
      return <span></span>;
    }
    else {
      return (
        <span className="pool_points_remaining">
          (+{this.props.pp} pool)
        </span>
      );
    }
  }
}

export default PoolPoints;
