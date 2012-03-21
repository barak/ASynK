##
## Created       : Tue Mar 13 14:26:01 IST 2012
## Last Modified : Wed Mar 21 17:31:25 IST 2012
##
## Copyright (C) 2012 Sriram Karra <karra.etc@gmail.com>
##
## Licensed under the GPL v3
##
## This file defines a wrapper class around a Google Contact entry, by
## extending the Contact abstract base Contact class. Using this class one can
## create and update contact entires in google contact folders, and manipulate
## properties, etc.
##

import sys, getopt, logging
import atom, gdata.contacts.data, gdata.contacts.client, base64

import utils
from   contact    import Contact

class GCContact(Contact):
    """This class extends the Contact abstract base class to wrap a Google
    Contact"""

    def __init__ (self, folder, con=None, gce=None):
        Contact.__init__(self, folder, con)

        self.set_gce(gce)
        if gce:
            self.init_props_from_gce(gce)

    ##
    ## First the inherited abstract methods from the base classes
    ##

    def save (self):
        """Saves the current contact on the server. For now we are only
        handling a new contact creation scneario. The protocol for updates is
        different"""

        ## FIXME: Handle the case of updating an existing contact's details.

        gce   = self.init_gce_from_props()
        entry = self.get_db().get_gdc().CreateContact(gce)

        if entry:
            logging.debug('Creation Successful!')
            logging.debug('ID for the new contact: %s', entry.id.text)
            self.set_itemid(entry.id.text)
        else:
            logging.error('Contact creation error.')
            return None

        return entry.id.text

    ##
    ## Now onto the non-abstract methods.
    ##

    def get_gce (self):
        gce = self._get_prop('gce')
        if gce:
            return gce

        return self.init_gce_from_props()

    def set_gce (self, gce):
        return self._set_prop('gce', gce)

    def init_props_from_gce (self, gce):
        self._snarf_itemid_from_gce(gce)
        self._snarf_names_gender_from_gce(gce)
        self._snarf_notes_from_gce(gce)
        self._snarf_emails_from_gce(gce)
        self._snarf_postal_from_gce(gce)
        self._snarf_org_details_from_gce(gce)
        self._snarf_phones_and_faxes_from_gce(gce)
        self._snarf_dates_from_gce(gce)
        self._snarf_websites_from_gce(gce)
        self._snarf_ims_from_gce(gce)

        self._snarf_custom_props_from_gce(gce)

    def init_gce_from_props (self):
        gce = gdata.contacts.data.ContactEntry()

        self._add_itemid_to_gce(gce)
        self._add_names_gender_to_gce(gce)
        self._add_notes_to_gce(gce)
        self._add_group_membership_to_gce(gce)
        self._add_emails_to_gce(gce)
        self._add_postal_to_gce(gce)
        self._add_org_details_to_gce(gce)
        self._add_phones_and_faxes_to_gce(gce)
        self._add_dates_to_gce(gce)
        self._add_websites_to_gce(gce)
        self._add_ims_to_gce(gce)

        self._add_custom_props_to_gce(gce)

        return self.set_gce(gce)

    def __str__ (self):
        ret = ''

        props = self.get_prop_names()
        for prop in props:
            ret += '%18s: %s\n' % (prop, self._get_prop(prop))

        return ret

    ##
    ## Internal functions that are not inteded to be called from outside.
    ##

    def _snarf_itemid_from_gce (self, ce):
        if ce.id:
            self.set_itemid(ce.id.text)

    def _snarf_names_gender_from_gce (self, ce):
        if ce.name:
            if ce.name.family_name:
                self.set_lastname(ce.name.family_name.text)

            if ce.name.given_name:
                self.set_firstname(ce.name.given_name.text)

            if ce.name.full_name:
                self.set_name(ce.name.full_name.text)
                # The FileAs property is required for Outlook. So we need to
                # keep this around
                self.set_fileas(ce.name.full_name.text)

            if ce.name.name_prefix:
                self.set_prefix(ce.name.name_prefix.text)

            if ce.name.name_suffix:
                self.set_suffix(ce.name.name_suffix.text)

        if ce.nickname:
            self.set_nickname(ce.nickname.text)

        if ce.gender:
            self.set_gender(ce.gender.value)

    def _snarf_notes_from_gce (self, ce):
        if ce.content and ce.content.text:
            self.set_notes(ce.content.text)

    def _snarf_emails_from_gce (self, ce):
        """Fetch the email entries in the specified ContactEntry object and
        populate them in the internal email address strutures."""

        ## FIXME: Need to figure out a way to identify and track the primary
        ## email address from the contact entry 'primary' field.

        if ce.email:
            for email in ce.email:
                if email.rel and email.address:
                    if email.rel == gdata.data.WORK_REL:
                        self.add_email_work(email.address)
                    elif email.rel == gdata.data.HOME_REL:
                        self.add_email_home(email.address)
                    elif email.rel == gdata.data.OTHER_REL:
                        self.add_email_other(email.address)

    def _snarf_postal_from_gce (self, ce):
        if ce.structured_postal_address:
            # FIXME: Need to implement this
            pass

    def _snarf_org_details_from_gce (self, ce):
        if ce.organization:
            if ce.organization.name and ce.organization.name.text:
                self.set_company(ce.organization.name.text)

            if ce.organization.title and ce.organization.title.text:
                self.set_title(ce.organization.title.text)

            if ce.organization.department:
                self.set_dept(ce.organization.department.text)

    def _snarf_phones_and_faxes_from_gce (self, ce):
        if ce.phone_number:
            for ph in ce.phone_number:
                if not ph.text:
                    continue

                if ph.rel == gdata.data.HOME_REL:
                    self.add_phone_home(ph.text)
                elif ph.rel == gdata.data.WORK_REL:
                    self.add_phone_work(ph.text)
                elif ph.rel == gdata.data.OTHER_REL:
                    self.add_phone_other(ph.text)
                elif ph.rel == gdata.data.MOBILE_REL:
                    self.add_phone_mob(ph.text)

                elif ph.rel == gdata.data.HOME_FAX_REL:
                    self.add_fax_home(ph.text)
                elif ph.rel == gdata.data.WORK_FAX_REL:
                    self.add_fax_work(ph.text)

                if ph.primary == 'true':
                    if ph.rel in [gdata.data.HOME_REL, gdata.data.WORK_REL,
                                  gdata.data.OTHER_REL, gdata.data.MOBILE_REL]:
                        self.set_phone_prim(ph.text)
                    elif ph.rel in [gdata.data.HOME_FAX_REL,
                                    gdata.data.WORK_FAX_REL]:
                        self.set_fax_prim(ph.text)

    def _snarf_dates_from_gce (self, ce):
        if ce.birthday and ce.birthday.when:
            self.set_birthday(ce.birthday.when)

        if ce.event and len(ce.event) > 0:
            ann = utils.get_event_rel(ce.event, 'anniversary')
            if ann:
                self.set_anniv(ann.start)

    def _snarf_websites_from_gce (self, ce):
        if ce.website:
            for site in ce.website:
                if site.rel == 'home-page':
                    self.add_web_home(site.href)
                elif site.rel == 'work':
                    self.add_web_work(site.href)

    def _snarf_ims_from_gce (self, ce):
        ## FIXME: Implement this routine
        pass

    def _snarf_custom_props_from_gce (self, ce):
        logging.error("_snarf_custom_props(): Not Implemented Yet")

    def _is_valid_phone_number (self, phone, type, name):
        phone = phone.strip()
        valid = True
        if (phone == '' or phone == '-' or phone == '_'):
            valid = False

        if not valid:
            logging.info('Invalid %12s number for contact %s. Skipping field',
                         type, name)

        return valid

    def _add_itemid_to_gce (self, gce):
        itemid = self.get_itemid()
        if itemid:
            gce.id = atom.data.Id(text=gcid)

    def _add_names_gender_to_gce (self, gce):
        """Populate the Name fields in gce, which is a Google ContactEntry
        object. Values for the name fields are obtained from the current
        objects property fields that should have been set earlier"""

        n = gdata.data.Name()

        text = self.get_firstname()
        if text:
            n.given_name = gdata.data.GivenName(text=text)

        text = self.get_lastname()
        if text:
            n.family_name = gdata.data.FamilyName(text=text)

        text = self.get_name()
        print 'name: ', text
        if text:
            n.full_name = gdata.data.FullName(text=text)

        text = self.get_suffix()
        if text:
            n.name_suffix = gdata.data.NameSuffix(text=text)

        text = self.get_suffix()
        if text:
            n.name_prefix = gdata.data.NamePrefix(text=text)

        gce.name = n

        text = self.get_nickname()
        if text:
            gce.nickname = gdata.contacts.data.NickName(text=text)

        text = self.get_gender()
        if text:
            gce.gender = gdata.data.Gender(text=text)


    def _add_notes_to_gce (self, gce):
        """Append the Notes field to the specified ContactEntry object. As of
        now only the first Notes entry is copied. In future the remaining
        ones will be mapped into the custom fields section."""

        ## FIXME: Do something about the other entries if any

        notes = self.get_notes()
        if notes:
            gce.content = atom.data.Content(text=notes[0])

    def _add_group_membership_to_gce (self, gce):
        """Append the group IDs that denote group membership to the specified
        ContactEntry object."""

        ## FIXME: Deal explicitly with the multi-group membership issue. As
        ## things are now, it is a recipe for infomration loss sooner or
        ## later. One approach to dealing with the situation is to explicitly
        ## have a gids flag in the Contact properties which can be suitably
        ## populated when the contact is created from a ContactEntry
        ## object. Er, actually that sounds blindingly obvious :-)

        gid = self.get_folder().get_itemid()
        gidm = gdata.contacts.data.GroupMembershipInfo(href=gid)
        gce.group_membership_info.append(gidm)

    def _add_emails_to_gce (self, gce):
        """Append the email addresses from the current Contact object to the
        specified ContactEntry object."""

        email_prim = self.get_email_prim()

        for email in self.get_email_home():
            prim = 'true' if email == email_prim else 'false'
            em = gdata.data.Email(address=email, primary=prim,
                                  rel=gdata.data.HOME_REL)
            gce.email.append(em)

        for email in self.get_email_work():
            prim = 'true' if email == email_prim else 'false'
            em = gdata.data.Email(address=email, primary=prim,
                                  rel=gdata.data.WORK_REL)
            gce.email.append(em)

        for email in self.get_email_other():
            prim = 'true' if email == email_prim else 'false'
            em = gdata.data.Email(address=email, primary=prim,
                                  rel=gdata.data.OTHER_REL)
            gce.email.append(em)


    def _add_postal_to_gce (self, gce):
        """Insert the address fields from current contact object into the
        ContactEntry object."""

        ## FIXME: This is an abominable 'placeholder' of a hack. We should
        ## really handle all sorts of addresses not just HOME addresses, and
        ## also deal with the structured nature of these addresses as Google
        ## itself provides some amount of support

        postal = self.get_postal()
        if postal:
            strt = gdata.data.Street(text=postal)
            add  = gdata.data.StructuredPostalAddress(
                street=strt, primary='true', rel=gdata.data.HOME_REL)

            gce.structured_postal_address = [add]

    def _add_org_details_to_gce (self, gce):
        """Insert the contact's company, department and other such
        organization details into the specified ContactEntry."""

        company = self.get_company()
        title   = self.get_title()
        dept    = self.get_dept()

        on = gdata.data.OrgName(text=company)    if company else None
        ot = gdata.data.OrgTitle(text=title)     if title   else None
        od = gdata.data.OrgDepartment(text=dept) if dept    else None

        org = gdata.data.Organization(primary='true', name=on, title=ot,
                                      department=od, rel=gdata.data.WORK_REL)
        gce.organization = org


    def _add_phones_and_faxes_to_gce (self, gce):
        """Append the contact's phone details into the specified ContactEntr
        object."""

        ph_prim = self.get_phone_prim()

        for ph in self.get_phone_home():
            prim = 'true' if ph == ph_prim else 'false'
            phone = gdata.data.PhoneNumber(text=ph, primary=prim,
                                           rel=gdata.data.HOME_REL)
            gce.phone_number.append(phone)

        for ph in self.get_phone_work():
            prim = 'true' if ph == ph_prim else 'false'
            phone = gdata.data.PhoneNumber(text=ph, primary=prim,
                                           rel=gdata.data.WORK_REL)
            gce.phone_number.append(phone)

        for ph in self.get_phone_other():
            prim = 'true' if ph == ph_prim else 'false'
            phone = gdata.data.PhoneNumber(text=ph, primary=prim,
                                           rel=gdata.data.OTHER_REL)
            gce.phone_number.append(phone)

        for ph in self.get_phone_mob():
            prim = 'true' if ph == ph_prim else 'false'
            phone = gdata.data.PhoneNumber(text=ph, primary=prim,
                                           rel=gdata.data.MOBILE_REL)
            gce.phone_number.append(phone)

        fax_prim = self.get_fax_prim()

        for fa in self.get_fax_home():
            prim = 'true' if fa == fax_prim else 'false'
            fax  = gdata.data.PhoneNumber(text=ph, primary=prim,
                                          rel=gdata.data.HOME_FAX_REL)
            gce.phone_number.append(fax)

        for fa in self.get_fax_work():
            prim = 'true' if fa == fax_prim else 'false'
            fax  = gdata.data.PhoneNumber(text=ph, primary=prim,
                                          rel=gdata.data.WORK_FAX_REL)
            gce.phone_number.append(fax)

    def _add_dates_to_gce (self, gce):
        """Append the date entries such as birthday and anniversary to the
        specified ContactEntry"""

        dt = self.get_birthday()
        if dt:
            gce.birthday = gdata.contacts.data.Birthday(when=dt)

        dt = self.get_anniv()
        if dt:
            date = gdata.data.When(start=dt)
            ann  = gdata.contacts.data.Event(when=date, rel='anniversary')
            gce.event.append(ann)

    def _add_websites_to_gce (self, gce):
        """Append any Web URLs from the current contact to the specified
        ContatEntry object."""

        web_prim = self.get_web_prim()

        for web in self.get_web_home():
            prim = 'true' if web == web_prim else 'false'
            home = gdata.contacts.data.Website(href=web, primary=prim,
                                               rel='home-page')
            gce.website.append(home)

        for web in self.get_web_work():
            prim = 'true' if web == web_prim else 'false'
            work = gdata.contacts.data.Website(href=web, primary=prim,
                                               rel='work')
            gce.website.append(work)

    def _add_ims_to_gce (self, gce):
        pass

    def _add_custom_props_to_gce (self, gce):
        ## FIXME: This needs to get implemented on priority. This is where all
        ## the sync tags and stuff will get stored.
        logging.error("_add_custom_props(): Not Implemented Yet")

    ##
    ## Temporarily placing keeping this stuff here while we start by cleaning
    ## up pimdb_gc.py
    ##

    # ## We will delete this guy very soon.

    # def add_olid_to_ce (self, ce, olid, replace=True):
    #     """Insert the Outlook EntryID for a contact as a  userdefined property
    #     in the Google ContactEntry and returned the modified ContactEntry.

    #     olid is the values as returned by GetProps - and, as a result a binary
    #     value. We base64 encode it before inserting into ContactEntry.

    #     If replace is True, then the first existing olid entry (if any) will
    #     be replaced with teh provided value. If it is False, then it is
    #     appended to existing list."""

    #     entryid_b64 = base64.b64encode(olid)
    #     ud       = gdata.contacts.data.UserDefinedField()
    #     ud.key   = 'olid'
    #     ud.value = entryid_b64

    #     if replace and len(ce.user_defined_field) > 0:
    #         ce.user_defined_field.pop()

    #     ce.user_defined_field.append(ud)

    #     return ce

def main ():
    tests = TestGCContact()
    tests.test_fetch_group_entries()

class TestGCContact:
    def __init__ (self):
        from   pimdb_gc   import GCPIMDB
        from   state      import Config

        config = Config('../app_state.json')
        # The following is the 'Gout' group on karra.etc@gmail.com
        self.gid = 'http://www.google.com/m8/feeds/groups/karra.etc%40gmail.com/base/41baff770f898d85'

        # Parse command line options
        try:
            opts, args = getopt.getopt(sys.argv[1:], '', ['user=', 'pw='])
        except getopt.error, msg:
            print 'python gc_wrapper.py --user [username] --pw [password]'
            sys.exit(2)

        user = ''
        pw = ''
        # Process options
        for option, arg in opts:
            if option == '--user':
                user = arg
            elif option == '--pw':
                pw = arg

        while not user:
            user = raw_input('Please enter your username: ')

        while not pw:
            pw = raw_input('Password: ')
            if not pw:
                print 'Password cannot be blank'

        try:
            self.pimdb = GCPIMDB(config, user, pw)
        except gdata.client.BadAuthentication:
            print 'Invalid credentials. WTF.'
            raise

    def find_group (self, gid):
        #    sample.print_groups()
        self.gout, ftype = self.pimdb.find_folder(gid)
        if self.gout:
            print 'Found the sucker. Name is: ', self.gout.get_name()
            return self.gout
        else:
            print 'D''oh. Folder not found.'
            return

    def test_create_contact (self, f=None):
        if not f:
            f = self.gout

        c = GCContact(f)
        c.set_name("ScrewBall Joseph")

        cid = c.save()
        if cid:
            print 'Successfully added contact. ID: ', cid
        else:
            print 'D''oh. Failed.'

    def get_folder_contacts (self, f, cnt=0):
        """A thought out version of this routine will eventually go as a
        method of GCFolder class.."""

        logging.info('Querying Google for status of Contact Entries...')

        updated_min = f.get_config().get_last_sync_stop('gc', 'ol')
        feed = f._get_group_feed(updated_min=updated_min, showdeleted='false')

        logging.info('Response recieved from Google. Processing...')

        if not feed.entry:
            logging.info('No entries in feed.')
            return

        contacts = []
        for i, entry in enumerate(feed.entry):
            c = GCContact(f, gce=entry)
            contacts.append(c)

        return contacts

    def test_fetch_group_entries (self, gid=None):
        if not gid:
            gid = self.gid

        f  = self.find_group(gid)
        cs = self.get_folder_contacts(f)
        print 'Got %d entries\n' % len(cs)
        for i, c in enumerate(cs):
            print 'Contat No %d: ' % i
            print str(c)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    main()
