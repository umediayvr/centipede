import json
import sys
import os

def dailyVersion(tk, ctx, sgPublishes, content):
    """
    Create a version in Shotgun for this path and linked to this publish.
    """
    # get current shotgun user
    currentUser = sgtk.util.get_current_user(tk)

    # create a name for the version based on the file name
    # grab the file name, strip off extension
    name = os.path.splitext(os.path.basename(content['movieFilePath']))[0]
    # do some replacements
    name = name.replace("_", " ")
    # and capitalize
    name = name.capitalize()

    # Create the version in Shotgun
    data = {
        "code": name,
        "sg_status_list": "rev",
        "entity": ctx.entity,
        "sg_first_frame": content['firstFrame'],
        "sg_last_frame": content['lastFrame'],
        "frame_count": (content['lastFrame'] - content['firstFrame'] + 1),
        "frame_range": "%s-%s" % (content['firstFrame'], content['lastFrame']),
        "sg_frames_have_slate": False,
        "created_by": currentUser,
        "user": currentUser,
        "description": content['comment'],
        "sg_path_to_frames": content['sequenceNameFormated'],
        "sg_movie_has_slate": True,
        "project": ctx.project
    }

    data["published_files"] = sgPublishes
    data["sg_path_to_movie"] = content['movieFilePath']

    sgVersion = tk.shotgun.create("Version", data)

    # upload files
    tk.shotgun.upload("Version", sgVersion["id"], content['movieFilePath'], "sg_uploaded_movie")
    tk.shotgun.upload_thumbnail("Version", sgVersion["id"], content['thumbnailFilePath'])

    return sgVersion

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

    tk = sgtk.sgtk_from_path(content['sequenceNameFormated'])
    ctx = tk.context_from_path(content['sequenceNameFormated'])
    sgtk.platform.start_engine('tk-shell', tk, ctx)
    sgtk.platform.change_context(ctx)

    sgPublish = sgtk.util.register_publish(
        tk,
        ctx,
        content['sequenceNameFormated'],
        content['name'],
        content['version'],
        comment=content['comment'],
        thumbnail_path=content['thumbnailFilePath'],
        published_file_type=content['publishedFileType']
    )

    # daily
    dailyVersion(
        tk,
        ctx,
        [sgPublish],
        content
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
