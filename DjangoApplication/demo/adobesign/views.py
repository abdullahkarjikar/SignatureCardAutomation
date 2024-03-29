import logging

from adobesign.backend import DemoAdobeSignBackend
from adobesign.models import Signer
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView, \
    RedirectView
from django.views.generic.detail import SingleObjectMixin
from time import sleep

from django_adobesign.client import AdobeSignClient, AdobeSignOAuthSession
from django_adobesign.exceptions import AdobeSignException
from django_adobesign.exceptions import AdobeSignNoMoreSignerException
from django_adobesign.views import SignerReturnView
from .models import Signature, SignatureType

ADOBESIGN_ACCOUNT_TYPE = 'self'


def get_adobesign_backend(signature_type, api_user=None,
                          on_behalf_of_user=None):
    adobe_client = AdobeSignClient(root_url=signature_type.api_root_url,
                                   access_token=signature_type.access_token,
                                   api_user=api_user,
                                   on_behalf_of_user=on_behalf_of_user)
    return DemoAdobeSignBackend(adobe_client)


class SettingsCreate(CreateView):
    model = SignatureType
    fields = ['web_root_url', 'application_id', 'application_secret']
    success_url = "/"

    def form_valid(self, form):
        ret = super(SettingsCreate, self).form_valid(form)
        self.object.signature_backend_code = 'adobesign'
        self.object.save()
        return ret


class SettingsUpdate(UpdateView):
    model = SignatureType
    fields = ['web_root_url', 'application_id', 'application_secret']
    success_url = "/"


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_agreements(self, signature_type):
        backend = get_adobesign_backend(signature_type)
        return backend.get_agreements(3)['userAgreementList']

    def get_next_signer_with_retry(self, backend, signature_id, nb_try=5,
                                   wait=1):

        for i in range(0, nb_try):
            try:
                return backend.get_next_signer_url(signature_id)
            except AdobeSignNoMoreSignerException as e:
                logging.warning(e)
                return None, None
            except AdobeSignException:
                sleep(wait)
        return None, None

    def get_signers_status(self, signature_id, signature_type):
        signers = []
        if signature_id:
            backend = get_adobesign_backend(signature_type)

            next_signer_mail, next_signer_url = \
                self.get_next_signer_with_retry(backend, signature_id,
                                                nb_try=1, wait=0)

            signers_data = backend.get_all_signers(signature_id)
            if 'participantSets' in signers_data:
                for signer_data in signers_data['participantSets']:
                    if 'name' in signer_data:
                        name = signer_data['name']
                    else:
                        name = signer_data['memberInfos'][0]['name']
                    email = signer_data['memberInfos'][0]['email']
                    url = next_signer_url \
                        if email == next_signer_mail else None
                    signers.append({'name': name,
                                    'status': signer_data['status'],
                                    'order': signer_data['order'],
                                    'mail': email,
                                    'url': url})
            signers.sort(key=lambda x: x['order'])
        return signers

    def get_latest_signature(self, signature_type):
        latest_signatures = []
        for signature in Signature.objects.all().order_by('-pk'):
            latest_signatures.append({
                'pk': signature.pk,
                'document_title': signature.document_title,
                'signature_backend_id': signature.signature_backend_id,
                'signers': self.get_signers_status(
                    signature.signature_backend_id, signature_type),
            })
            # Just for demo disply
            for signer in latest_signatures[-1]['signers']:
                db_signer = signature.signers.get(
                    signing_order=signer['order'], email=signer['mail'])
                signer['current_status'] = db_signer.current_status
                signer['signature_backend_id'] = db_signer.signature_backend_id
        return latest_signatures

    def get_context_data(self, **kwargs):
        data = super(HomeView, self).get_context_data(**kwargs)
        signature_type = SignatureType.objects.last()
        if signature_type:
            data['signature_type'] = signature_type
            data['agreements'] = []
            data['latest_signatures'] = []

            if signature_type.access_token:
                try:
                    data['agreements'] = self.get_agreements(signature_type)
                    data['latest_signatures'] = self.get_latest_signature(
                        signature_type)
                except AdobeSignException as e:
                    data['errors'] = e
                    print(e)

        return data


class TokenView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        code = self.request.GET.get('code')
        signature_type = SignatureType.objects.last()
        redirect_uri = self.request.build_absolute_uri(reverse('token'))
        adobesign_oauth_client = AdobeSignOAuthSession(
            redirect_uri=redirect_uri,
            application_id=signature_type.application_id,
            account_type=ADOBESIGN_ACCOUNT_TYPE)
        # Redirect user to AdobeSign authorization
        if not code:
            return adobesign_oauth_client.get_authorization_url(
                signature_type.web_root_url)
        # Create token

        token_response = adobesign_oauth_client.create_token(
            code, signature_type.application_secret)
        signature_type.access_token = token_response.get('access_token')
        signature_type.refresh_token = token_response.get('refresh_token')
        signature_type.api_root_url = self.request.GET.get('api_access_point')
        signature_type.save()
        return reverse('home')


class RefreshTokenView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        signature_type = SignatureType.objects.last()
        # Refresh token
        refresh_token_resp = AdobeSignOAuthSession.refresh_token(
            signature_type.refresh_token,
            signature_type.application_id,
            signature_type.application_secret)
        signature_type.access_token = refresh_token_resp.get('access_token')
        signature_type.refresh_token = refresh_token_resp.get('refresh_token')
        signature_type.save()
        return reverse('home')


class CreateSignatureView(CreateView):
    model = Signature
    fields = ['document', 'document_title']
    success_url = reverse_lazy('signer')

    def get_form_kwargs(self):
        self.object = Signature(
            signature_type=SignatureType.objects.last())
        return super(CreateSignatureView, self).get_form_kwargs()


class CreateSigner(CreateView):
    model = Signer
    fields = ['signing_order', 'full_name', 'email']
    success_url = reverse_lazy('home')

    def get_initial(self):
        return {'signing_order': Signature.objects.last().signers.count() + 1}

    def form_valid(self, form):
        if 'saveadd' in self.get_form().data:
            self.success_url = reverse('signer')
        return super(CreateSigner, self).form_valid(form)

    def get_form_kwargs(self):
        self.object = Signer(signature=Signature.objects.last())
        return super(CreateSigner, self).get_form_kwargs()


class Sign(RedirectView, SingleObjectMixin):
    model = Signature

    def get_redirect_url(self, *args, **kwargs):
        signature = self.get_object()
        signature_type = signature.signature_type
        backend = get_adobesign_backend(signature_type)
        backend.create_signature(
            signature=signature,
            post_sign_redirect_url=self.request.build_absolute_uri(
                reverse('signed', kwargs={'pk': signature.pk})))
        return reverse('home')


class DemoSignerReturnView(SignerReturnView):
    def replace_document(self, signed_document):
        # Replace old document by signed one.
        filename = self.signature.document.name
        with open(filename, 'wb') as fd:
            fd.write(signed_document)

    def update_signer(self, signer, status, message=''):
        signer.current_status = status
        signer.save()

    def update_signature(self, status):
        self.signature.state = status
        self.signature.save()

    def get_signer_signed_url(self, status):
        return reverse('home')

    def get_signer_error_url(self, status):
        return reverse('home')

    def get_signer_canceled_url(self, status):
        return reverse('home')

    def has_already_signed(self, signer):
        return signer.current_status in ('COMPLETED', 'WAITING_FOR_OTHERS')
