import json
import sys

def publish(content):
    """
    Run the shotgun publish.
    """
    # create an authenticator object. This is the main object which
    # handles all authentication
    sa = sgtk.authentication.ShotgunAuthenticator()

    # Use the authenticator to create a user object. This object
    # identifies a Shotgun user or script and also wraps around
    # a Shotgun API instance which is associated with that user.
    user = sa.create_script_user(
        api_script="Toolkit",
        api_key="7839b54042ddfecdc6d0bd27e72c4499d5c04516f96dc1ff30d9bb7ac084ec7e",
        host="https://umedia.shotgunstudio.com"
    )

    # tell the Toolkit Core API which user to use
    sgtk.set_authenticated_user(user)

    tk = sgtk.sgtk_from_path(content['jsonFile'])
    projectEntity = tk.entity_from_path(tk.project_path)
    projectId = projectEntity.get("id")

    filters = [
        ['code', 'is', content['assetName']],
        ['project', 'is', {'type': 'Project', 'id': projectId}]
    ]
    assetData = tk.shotgun.find('Asset', filters)
    if len(assetData) != 1:
        sys.stderr.write(
            "[runTexturePublish] Cannot find unique asset {} in project {}. Skip Publish.".format(
                content['assetName'],
                projectEntity.get('name')
            )
        )
        return

    ctx = tk.context_from_entity_dictionary(assetData[0])
    sgtk.platform.start_engine('tk-shell', tk, ctx)
    sgtk.platform.change_context(ctx)

    sgtk.util.register_publish(
        tk,
        ctx,
        content['jsonFile'],
        content['name'],
        content['version'],
        comment=content['comment'],
        published_file_type=content['publishedFileType']
    )


if __name__ == "__main__":
    content = {}
    with open(sys.argv[1]) as jsonData:
        content = json.load(jsonData)

    # importing sgtk
    sys.path.insert(1, '/data/job/{0}/config/toolkit/install/core/python'.format(
            content['job']
        )
    )
    import sgtk

    # running publish
    publish(content)
