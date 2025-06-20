# {{ project_name if project_name else distribution_name }}

{{ project_short_description }}

{% if generate_docs != 'none' %}
The project documentation is available at [docs/](docs/).
{% endif %}

## Installation

> Write installation instructions here or remove this section.

## Usage

{% if package_type == 'cli' %}
```
{{ package_name.split('.')[-1] }} --help
```
{% endif %}

### Example

#### Installing Package from Private Registry

You have set up your project and want to install `my-superawesome-package` from `https://your.super.secret.com/package/repository/pypi/simple`.
One way to handle this is to add credentials to your .env file like this:

```bash
echo "UV_INDEX_SUPER_SECRET_REPO_USERNAME=clark" >> .env
echo "UV_INDEX_SUPER_SECRET_REPO_PASSWORD=kent" >> .env
```

If you are using `direnv` adding these to the `.env` file you can autoload them by pressing `enter` in the terminal. Once the new environment variables are exported, you can add your super secret package like this:

```bash
uv add my-superawesome-package --index super-secret-repo=https://your.super.secret.com/package/repository/pypi/simple
```

> Remember that the name of your index (super-secret-repo) and the name of the environment have to match. When searching for credentials `uv` will automatically search for environment variables which include the index name, but will make it uppercase and replace dashes (-) with underscores (_).

In case this package repository should _only_ be used for specific packages you'll need to add `explicit = true` under the `[[tool.uv.index]]` section of your newly added index.
For a full explanation of configuring custom indexes and other authentication methods have a look at the [astral documentation page](https://docs.astral.sh/uv/concepts/projects/dependencies/#index).

{% if generate_dockerfile %}

### Building a Docker image

The template comes pre-packaged with a dockerfile which uses multi-stage builds to build light-weight images. Due to the use of multi-stage builds and the use of `--mount` to mount secrets, this supports installing packages from private package registries. Below is an example of how you can build a docker image that can install packages from a private package registry (this assumes you've followed the steps described in [the previous section](#installing-package-from-private) and have run `uv sync`)

```bash
docker build \
  --secret id=dotenv,src=.env \
  -t testing:with-env .
```
{% endif %}

## License

This project is licensed under the terms of the [{{ license }}](LICENSE).
