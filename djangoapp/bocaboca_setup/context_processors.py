from bocaboca_setup.models import BocabocaSetup

def bocaboca_setup(request):
    setup = BocabocaSetup.objects.order_by('-id').first()
    return{
        'bocaboca_setup': setup
    }