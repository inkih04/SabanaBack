from rest_framework import serializers
from django.contrib.auth.models import User

from .StatusSerializer import StatusSerializer
from .PrioritiesSerializer import PrioritiesSerializer
from .TypesSerializer import TypesSerializer
from .SeveritiesSerializer import SeveritiesSerializer
from .UserSerializer import UserSerializer
from .AttachmentSerializer import AttachmentSerializer
from .CommentSerializer import CommentSerializer
from issues.models import Status, Priorities, Types, Severities, Issue, Attachment


class IssueSerializer(serializers.ModelSerializer):
    status            = StatusSerializer(read_only=True)
    status_id         = serializers.PrimaryKeyRelatedField(queryset=Status.objects.all(),
                                                           source='status', write_only=True, required=False)
    status_name       = serializers.CharField(write_only=True, required=False)

    priority          = PrioritiesSerializer(read_only=True)
    priority_id       = serializers.PrimaryKeyRelatedField(queryset=Priorities.objects.all(),
                                                           source='priority', write_only=True, required=False)
    priority_name     = serializers.CharField(write_only=True, required=False)

    severity          = SeveritiesSerializer(read_only=True)
    severity_id       = serializers.PrimaryKeyRelatedField(queryset=Severities.objects.all(),
                                                           source='severity', write_only=True, required=False)
    severity_name     = serializers.CharField(write_only=True, required=False)

    issue_type        = TypesSerializer(read_only=True)
    issue_type_id     = serializers.PrimaryKeyRelatedField(queryset=Types.objects.all(),
                                                           source='issue_type', write_only=True, required=False)
    issue_type_name   = serializers.CharField(write_only=True, required=False)

    assigned_to       = UserSerializer(read_only=True)
    assigned_to_id    = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),
                                                           source='assigned_to',
                                                           write_only=True, required=False, allow_null=True)
    assigned_to_username = serializers.CharField(write_only=True, required=False, allow_blank=True)

    created_by        = UserSerializer(read_only=True)

    watchers          = UserSerializer(read_only=True, many=True)
    watchers_ids      = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),
                                                           source='watchers', many=True,
                                                           write_only=True, required=False, allow_null=True)
    watchers_usernames = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        write_only=True,
        required=False,
        allow_null=True,
        default=list,
        allow_empty=True,
        style={'base_template': 'input.txt'}  # Esto ayuda con form-data
    )

    # **Nuevo campo para OpenAPI 3.0**: lista opcional de archivos
    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        allow_empty=True,
        default=list,
        help_text="Lista de ficheros a adjuntar (opcional)"
    )

    attachment = AttachmentSerializer(many=True, read_only=True)
    comments   = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = [
            'id', 'subject', 'description', 'created_at', 'due_date',
            'status', 'status_id', 'status_name',
            'priority', 'priority_id', 'priority_name',
            'severity', 'severity_id', 'severity_name',
            'issue_type', 'issue_type_id', 'issue_type_name',
            'assigned_to', 'assigned_to_id', 'assigned_to_username',
            'created_by',
            'watchers', 'watchers_ids', 'watchers_usernames',
            'files',
            'attachment', 'comments',
        ]
        read_only_fields = ['created_at', 'created_by']

    def validate(self, data):
        if 'status_name' in self.initial_data:
            status_name = self.initial_data['status_name']
            if status_name:
                try:
                    status = Status.objects.get(nombre=self.initial_data['status_name'])
                    data['status'] = status
                except Status.DoesNotExist:
                    raise serializers.ValidationError(
                        {"status_name": f"No existe Status con nombre '{self.initial_data['status_name']}'"})

        if 'assigned_to_username' in self.initial_data:
            username = self.initial_data['assigned_to_username']
            if username in [None, ""]:
                data['assigned_to'] = None
            else:
                try:
                    user = User.objects.get(username=username)
                    data['assigned_to'] = user
                except User.DoesNotExist:
                    raise serializers.ValidationError({
                        "assigned_to_username": f"No existe usuario con username '{username}'"
                    })

            # Procesamos campos por nombre para Priority
        if 'priority_name' in self.initial_data :
            priority_name = self.initial_data['priority_name']
            if priority_name:
                try:
                    priority = Priorities.objects.get(nombre=self.initial_data['priority_name'])
                    data['priority'] = priority
                except Priorities.DoesNotExist:
                    raise serializers.ValidationError(
                        {"priority_name": f"No existe Priority con nombre '{self.initial_data['priority_name']}'"})

            # Procesamos campos por nombre para Severity
        if 'severity_name' in self.initial_data:
            severity_name = self.initial_data['severity_name']
            if severity_name:
                try:
                    severity = Severities.objects.get(nombre=self.initial_data['severity_name'])
                    data['severity'] = severity
                except Severities.DoesNotExist:
                    raise serializers.ValidationError(
                        {"severity_name": f"No existe Severity con nombre '{self.initial_data['severity_name']}'"})

            # Procesamos campos por nombre para Type
        if 'issue_type_name' in self.initial_data:
            issue_type_name = self.initial_data['issue_type_name']
            if issue_type_name:
                try:
                    issue_type = Types.objects.get(nombre=self.initial_data['issue_type_name'])
                    data['issue_type'] = issue_type
                except Types.DoesNotExist:
                    raise serializers.ValidationError(
                        {"issue_type_name": f"No existe Type con nombre '{self.initial_data['issue_type_name']}'"})

            # Procesamos campo por username para assigned_to
        if 'assigned_to_username' in self.initial_data and self.initial_data['assigned_to_username']:
            try:
                user = User.objects.get(username=self.initial_data['assigned_to_username'])
                data['assigned_to'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    "assigned_to_username": f"No existe usuario con username '{self.initial_data['assigned_to_username']}'"})

            # Procesamos campos por username para watchers
        if 'watchers_usernames' in self.initial_data:
            usernames = self.initial_data['watchers_usernames']
            print(f"\nVALIDATING USERNAMES: {usernames}, TYPE: {type(usernames)}")

            # Handle different types of input
            if isinstance(usernames, str):
                print("Username is string, splitting by comma")
                username_list = [u.strip() for u in usernames.split(',') if u.strip()]
            elif isinstance(usernames, list):
                print("Username is already a list")
                username_list = usernames
            else:
                print(f"Username is unexpected type: {type(usernames)}")
                username_list = []

            print(f"Processed username_list: {username_list}")

            watchers = []
            for username in username_list:
                print(f"CHECKING USERNAME: '{username}'")
                try:
                    user = User.objects.get(username=username)
                    print(f"Found user: {user.username} (ID: {user.id})")
                    watchers.append(user)
                except User.DoesNotExist:
                    print(f"ERROR: User '{username}' not found")
                    raise serializers.ValidationError(
                        {"watchers_usernames": f"No existe usuario con username '{username}'"})
            if watchers:
                print(f"Setting watchers: {[w.username for w in watchers]}")
                data['watchers'] = watchers

        print(f"Final validated data keys: {data.keys()}")
        print("==== VALIDATE END ====\n")

        return data

    def create(self, validated_data):
        # Remove the fields that aren't in the Issue model
        files = validated_data.pop('files', [])
        watchers = validated_data.pop('watchers', [])

        # Remove these fields as they're not model fields
        validated_data.pop('assigned_to_username', None)
        validated_data.pop('watchers_usernames', None)
        validated_data.pop('status_name', None)
        validated_data.pop('priority_name', None)
        validated_data.pop('severity_name', None)
        validated_data.pop('issue_type_name', None)

        # Asegúrate de que created_by no esté duplicado
        if 'created_by' in validated_data:
            validated_data.pop('created_by')

        issue = Issue.objects.create(**validated_data, created_by=self.context['request'].user)

        if watchers:
            issue.watchers.set(watchers)
        for f in files:
            Attachment.objects.create(issue=issue, file=f)
        return issue

    def update(self, instance, validated_data):
        print("\n==== UPDATE START ====")
        print(f"Validated data keys: {validated_data.keys()}")

        files = validated_data.pop('files', [])
        print(f"Files: {files}")

        watchers = validated_data.pop('watchers', None)
        if watchers is not None:
            print(f"Watchers: {[w.username for w in watchers]}")
            instance.watchers.set(watchers)  # <--- ¡Faltaba esto!
        else:
            print("Watchers is None - will not update")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        print("==== UPDATE END ====\n")
        return instance

    def to_internal_value(self, data):
        print("\n==== TO_INTERNAL_VALUE START ====")
        print(f"Original data type: {type(data)}")
        print(f"Original data content: {data}")

        data_copy = data.copy()
        print(f"Data copy type: {type(data_copy)}")

        # Fix processing of watchers_usernames
        if 'watchers_usernames' in data:
            print(f"\nFound watchers_usernames in data")
            print(f"watchers_usernames type: {type(data.get('watchers_usernames'))}")
            print(f"watchers_usernames raw value: '{data.get('watchers_usernames')}'")

            if hasattr(data, 'getlist'):
                print("Data has getlist method (likely QueryDict)")
                username_items = data.getlist('watchers_usernames')
                print(f"username_items from getlist: {username_items}")
                print(f"username_items type: {type(username_items)}")

                if username_items:
                    print(f"First item type: {type(username_items[0])}")
                    print(f"First item value: '{username_items[0]}'")

                    if len(username_items) == 1 and isinstance(username_items[0], str) and ',' in username_items[0]:
                        print("Single comma-separated item detected")
                        usernames = [u.strip() for u in username_items[0].split(',') if u.strip()]
                        print(f"Split usernames: {usernames}")
                        data_copy['watchers_usernames'] = usernames
                    else:
                        print("Multiple items or no commas detected")
                        data_copy['watchers_usernames'] = [u for u in username_items if u]
                        print(f"Processed username_items: {data_copy['watchers_usernames']}")
                else:
                    print("No items from getlist")
                    data_copy['watchers_usernames'] = []
            elif isinstance(data.get('watchers_usernames'), str):
                print("watchers_usernames is a string")
                if ',' in data.get('watchers_usernames'):
                    print("String contains commas")
                    usernames = [u.strip() for u in data.get('watchers_usernames').split(',') if u.strip()]
                    print(f"Split usernames: {usernames}")
                    data_copy['watchers_usernames'] = usernames
                elif data.get('watchers_usernames').strip():
                    print("String is single non-empty value")
                    data_copy['watchers_usernames'] = [data.get('watchers_usernames').strip()]
                    print(f"Single username array: {data_copy['watchers_usernames']}")
                else:
                    print("String is empty")
                    data_copy['watchers_usernames'] = []
            else:
                print(f"watchers_usernames is not a string: {type(data.get('watchers_usernames'))}")

            print(f"Final watchers_usernames value: {data_copy.get('watchers_usernames')}")
        else:
            print("No watchers_usernames in data")

        print("==== TO_INTERNAL_VALUE END ====\n")
        return super().to_internal_value(data_copy)
