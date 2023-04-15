/* eslint-disable jsx-a11y/anchor-is-valid */
import React from 'react';
import { Navbar, Nav } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faBluetoothB } from '@fortawesome/free-brands-svg-icons'

declare type SwitchActiveViewCB = (activeView: string) => void;

type NavbarProps = {
  activeView: string;
  switchActiveViewCB: SwitchActiveViewCB;
};

export default class NavigationBar extends React.Component<NavbarProps, any> {
  onSelect(selectedKey: string | null) {
    const { switchActiveViewCB } = this.props;
    if (selectedKey) switchActiveViewCB(selectedKey);
  }

  render() {
    const { activeView } = this.props;
    return (
      <>
          <Navbar bg="dark" variant="dark" className="navbar-expand px-3">
          <Nav
            className="me-auto"
            activeKey={activeView}
            onSelect={(selectedKey) => this.onSelect(selectedKey)}
          >
            <Nav.Link eventKey="Bt-Clients" className="me-auto">
              <FontAwesomeIcon icon={faBluetoothB} size="6x" className="text-primary d-inline-block align-middle px-2" /><span className="text-primary h5 align-middle" style={{ marginBottom: '0' }}>RPI-K(V)M</span>
            </Nav.Link>
          </Nav>
          <Nav
            activeKey={activeView}
            onSelect={(selectedKey) => this.onSelect(selectedKey)}
          >
            <Nav.Link eventKey="Settings" className="py-0">
              <i className="bi bi-gear-wide-connected text-secondary px-2" style={{ fontSize: '4.5rem' }} />
            </Nav.Link>
          </Nav>
        </Navbar>
      </>
    );
  }
}
