import React from 'react';
import { Button } from 'react-bootstrap';
import { ServerConfig  } from './Common';
import BtClientRemovalModalButton from './BtClientRemovalModalButton';

export type BtClientProps = {
  client: BtClientInfo;
  lastClientOrderNumber: number;
};

export type BtClientInfo = {
  name: string;
  address: string;
  isConnected: boolean;
  order: number;
  isHost: boolean;
};

export class BtClient extends React.Component<BtClientProps, any> {

  setAsActiveBtHost() {
    const { client } = this.props;
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clientAddress: client.address }),
    };

    fetch(
      `${ServerConfig.url}switch_active_bt_host`,
      requestOptions
    );
  }

  clearActiveBtHost() {
    const { client } = this.props;
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clientAddress: client.address }),
    };

    fetch(
      `${ServerConfig.url}clear_active_bt_host`,
      requestOptions
    );
  }

  changeOrderLower() {
    const { client } = this.props;
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        clientAddress: client.address,
        order_type: 'lower',
      }),
    };

    fetch(
      `${ServerConfig.url}change_client_order`,
      requestOptions
    );
  }

  changeOrderHigher() {
    const { client } = this.props;
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        clientAddress: client.address,
        order_type: 'higher',
      }),
    };

    fetch(
      `${ServerConfig.url}change_client_order`,
      requestOptions
    );
  }

  removeClient() {
    const { client } = this.props;
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clientAddress: client.address }),
    };

    fetch(`${ServerConfig.url}remove_client`, requestOptions);
  }

  changeConnectState() {
    const { client } = this.props;
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ clientAddress: client.address }),
    };
    const connectionApiEndpoint = client.isConnected
      ? 'disconnect_client'
      : 'connect_client';
    fetch(
      `${ServerConfig.url}${connectionApiEndpoint}`,
      requestOptions
    );
  }

  renderSwitchActiveBtHostButton() {
    const { client } = this.props;
    if (client.isHost) return <></>;
    return (
      <Button
        variant="primary"
        className="btn-huge"
        onClick={() => this.setAsActiveBtHost()}
      >
        Activate
      </Button>
    );
  }

  renderClearActiveBtHostButton() {
    const { client } = this.props;
    if (client.isHost) return (
      <Button
        variant="secondary"
        className="btn-huge"
        onClick={() => this.clearActiveBtHost()}
      >
        Deactivate
      </Button>
    );
  }

  renderOrderLowerButton() {
    const { client } = this.props;
    if (client.order > 0) {
      return (
        <Button
          variant="default"
          className="text-white col-1 py-0 pe-3"
          onClick={() => this.changeOrderLower()}
        >
          <i className="bi bi-chevron-left" style={{ fontSize: '2rem' }} />
        </Button>
      );
    }
    return (
      <Button
        variant="default"
        className="text-white col-1 py-0 pe-3 disabled"
        onClick={() => this.changeOrderLower()}
      >
        <i className="bi bi-chevron-left" style={{ fontSize: '2rem' }} />
      </Button>
    );
  }

  renderOrderHigherButton() {
    const { client, lastClientOrderNumber } = this.props;
    if (client.order < lastClientOrderNumber) {
      return (
        <Button
          variant="default"
          className="text-white col-1 py-0 pe-3"
          onClick={() => this.changeOrderHigher()}
        >
          <i className="bi bi-chevron-right" style={{ fontSize: '2rem' }} />
        </Button>
      );
    }
    return (
      <Button
        variant="default"
        className="text-white col-1 py-0 pe-3 disabled"
        onClick={() => this.changeOrderHigher()}
      >
        <i className="bi bi-chevron-right" style={{ fontSize: '2rem' }} />
      </Button>
    );
  }

  renderOrderButtons() {
    return (
      <div className="row">
        {this.renderOrderLowerButton()}
        {this.renderOrderHigherButton()}
      </div>
    );
  }

  renderConnectedCard() {
    const { client } = this.props;
    const isHostContent = client.isHost ? '(Active Host)' : '';

    return (
      <div className="col">
        <div className="card h-100 mb-3 bg-dark border-success">
          <div className="card-header bg-success d-flex align-items-center pb-0">
            {/* <div className="row"> */}
              <div className="text-center text-white col-2">
                {this.renderOrderButtons()}
              </div>
              <h5 className="text-center text-white fs-3 fw-bold col-8">{client.name}</h5>
            {/* </div> */}
          </div>
          <div className="card-body h-100 d-flex flex-column">
            {/* <h6 className="card-title">Connected {isHostContent}</h6> */}
            <p className="card-text fs-4 fw-bold">{client.address} {isHostContent}</p>
            <div className="d-grid h-100 gap-2">
              {this.renderSwitchActiveBtHostButton()}
              {this.renderClearActiveBtHostButton()}
              <Button
                variant="danger"
                className="btn-huge align-self-end"
                onClick={() => this.changeConnectState()}
              >
                Disconnect
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  renderDisconnectedCard() {
    const { client } = this.props;
    return (
      <div className="col">
        <div className="card h-100 mb-3 bg-dark border-secondary">
          <div className="card-header bg-secondary d-flex align-items-center pb-0">
            {/* <div className="row"> */}
              <div className="text-center text-white col-2">
                {this.renderOrderButtons()}
              </div>
              <h5 className="text-center text-white fs-3 col-8">{client.name}</h5>
              <div className="text-center text-white col-1 offset-1">
                <BtClientRemovalModalButton
                  name={client.name}
                  removeCB={() => this.removeClient()}
                />
              </div>
            {/* </div>  */}
          </div>
          <div className="card-body h-100 d-flex flex-column">
            {/* <h6 className="card-title">Disconnected</h6> */}
            <p className="card-text fs-4">{client.address}</p>
            <div className="d-grid h-100 gap-2">
              {this.renderSwitchActiveBtHostButton()}
              <Button
                variant="success"
                className="btn-huge align-self-end"
                onClick={() => this.changeConnectState()}
              >
                Connect
              </Button>
            </div>              
          </div>
        </div>
      </div>
    );
  }

  render() {
    const { client } = this.props;
    if (client.isConnected) {
      return this.renderConnectedCard();
    }
    return this.renderDisconnectedCard();
  }
}
