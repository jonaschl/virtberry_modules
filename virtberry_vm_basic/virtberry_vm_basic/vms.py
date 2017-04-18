#!/usr/bin/python3
from flask_login import login_required
from flask import Blueprint, render_template, abort, redirect, url_for, flash, Markup
from jinja2 import TemplateNotFound
import libvirt

def dom_state(libvirt_state):
    if libvirt_state == libvirt.VIR_DOMAIN_NOSTATE:
        state = "No state"
        return state
    elif libvirt_state == libvirt.VIR_DOMAIN_RUNNING:
        state = "Running"
        return state
    elif libvirt_state == libvirt.VIR_DOMAIN_BLOCKED:
        state = "Blocked"
        return state
    elif libvirt_state == libvirt.VIR_DOMAIN_PAUSED:
        state = "Paused"
        return state
    elif libvirt_state == libvirt.VIR_DOMAIN_SHUTDOWN:
        state = "Shutdown"
        return state
    elif libvirt_state == libvirt.VIR_DOMAIN_SHUTOFF:
        state = "Shutoff"
        return state
    elif libvirt_state == libvirt.VIR_DOMAIN_CRASHED:
        state = "Crashed"
        return state
    elif libvirt_state == libvirt.VIR_DOMAIN_PMSUSPENDED:
        state = "Suspend"
        return state
    else:
        state = "Unknown"
        return state





vms = Blueprint('vms', __name__, template_folder='templates')

@vms.route('/vm/<string:uuid>/actions/<string:action>')
@login_required
def action(uuid, action):
        import sys
        import libvirt
        try :
            conn = libvirt.open('qemu:///system')
        except BaseException as error:
            # Markup is only needed because of the <br>
            flash(Markup(u"Could not connect to  \"qemu:///system\". <br> {}".format(error)), 'alert-danger')
            print('Failed to open connection to qemu:///system', file=sys.stderr)
            return redirect("/vm")

        try:
            dom = conn.lookupByUUIDString(uuid)
        except:
            flash(u"Failed to get the domain object", 'alert-danger')
            print('Failed to get the domain object', file=sys.stderr)
            conn.close()
            return redirect("/vm")

        domname = dom.name()
        if action == "start":
            try:
                dom.create()
            except:
                flash(u"Can not boot guest domain.", 'alert-danger')
                print('Can not boot guest domain.', file=sys.stderr)
                conn.close()
                return redirect("/vm")

            flash(u"Sucessfully started Domain \"{}\"".format(domname), 'alert-info')
            conn.close()
            return redirect("/vm")

        elif action == "shutdown":
            try:
                dom.shutdown()
            except:
                flash(u"Can not shutdown guest domain.", 'alert-danger')
                print('Can not shutdown guest domain.', file=sys.stderr)
                conn.close()
                return redirect("/vm")

            flash(u"Sucessfully shutdowned Domain \"{}\"".format(domname), 'alert-info')
            conn.close()
            return redirect("/vm")

        elif action == "destroy":
            try:
                dom.destroy()
            except:
                flash(u"Can not destroy guest domain.", 'alert-danger')
                print('Can not destroy guest domain.', file=sys.stderr)
                conn.close()
                return redirect("/vm")

            flash(u"Sucessfully destroyed Domain \"{}\"".format(domname), 'alert-info')
            conn.close()
            return redirect("/vm")

        elif action == "pause":
            try:
                dom.suspend()
            except:
                flash(u"Can not pause guest domain.", 'alert-danger')
                print('Can not pause guest domain.', file=sys.stderr)
                conn.close()
                return redirect("/vm")

            flash(u"Sucessfully paused Domain \"{}\"".format(domname), 'alert-info')
            conn.close()
            return redirect("/vm")

        elif action == "resume":
            try:
                dom.resume()
            except:
                flash(u"Can not eesume guest domain.:", 'alert-danger')
                print('Can not resume guest domain.', file=sys.stderr)
                conn.close()
                return redirect("/vm")

            flash(u"Sucessfully resumed Domain \"{}\"".format(domname), 'alert-info')
            conn.close()
            return redirect("/vm")

        else:
            flash(u"No such action: \"{}\"".format(action), 'alert-warning')
            conn.close()
            return redirect("/vm")


@vms.route('/vm')
@login_required
def vm_overview():
    import sys
    import libvirt
    conn = libvirt.open('qemu:///system')
    doms = conn.listAllDomains(0)
    domains = []

    if len(doms) != 0:
        for dom in doms:
            domain = {}
            domain.setdefault("name", dom.name())
            domain.setdefault("uuid", dom.UUIDString())
            state, reason = dom.state()
            domain.setdefault("state", dom_state(state))
            domains.append(domain)

    conn.close()

    return render_template("virtberry_vm_basic-vm.html", domains=domains)
