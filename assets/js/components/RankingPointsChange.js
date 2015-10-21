import React, { Component } from 'react';

export class RankingPointsChange extends Component {
  render() {
    if (this.props.rp_change == 0) {
      return <span>(-)</span>;
    }
    else if (this.props.rp_change > 0) {
      return (
        <span className="change_positive">
          +{this.props.rp_change}
        </span>
      );
    } else {
      return (
        <span className="change_negative">
          {this.props.rp_change}
        </span>
      );
    }
  }
}

export default RankingPointsChange;
